import csv
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from jp_shorts.core import (KEYWORD_COLUMNS, CRITERIA, initialise, select, selected,
                            rank_niches, keyword_report, record_keyword, prepare_speech)
from jp_shorts.youtube import discover, seconds, verify, shortlist, YouTube
from elmarketing.jobs import write_json, digest
from elmarketing.captions import cues


def niche(identifier='fixture'):
    return {'id':identifier, 'name_ja':'試験用', 'name_en':'TEST FIXTURE ONLY',
            'audience_en':'Fixture', 'monetisation_en':'Not a commercial recommendation',
            'unknowns_en':'All real-world demand and earnings unknown',
            'assessment':{k:{'score':2,'rationale_en':'Synthetic fixture, not evidence'} for k in CRITERIA},
            'sources':[{'url':'https://example.com/fixture','accessed_on':'2026-01-01','supports':'Fixture only'}]}


class ResearchTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'project'
        initialise(self.root)

    def choose(self):
        write_json(self.root/'niches.json',{'niches':[niche(),niche('other')]})
        select(self.root,'fixture')

    def csv(self, rows):
        path=self.root/'keywords.csv'
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=KEYWORD_COLUMNS);w.writeheader();w.writerows(rows)
        return path

    def row(self, **changes):
        value=dict(zip(KEYWORD_COLUMNS,('試験','test','10','estimated_monthly_searches','YouTube','JP','ja','2026-01','fixture','https://example.com/data','2026-02-01')))
        value.update(changes)
        return value

    def test_niche_choice_required_and_cannot_be_silently_changed(self):
        with self.assertRaises(ValueError): selected(self.root)
        self.choose()
        self.assertEqual(selected(self.root)['selected_niche']['id'],'fixture')
        with self.assertRaises(ValueError):select(self.root,'other')
        with self.assertRaises(FileExistsError):initialise(self.root)

    def test_no_source_or_invalid_score_rejected(self):
        row=niche();row['sources']=[]
        with self.assertRaises(ValueError):rank_niches({'niches':[row]})
        row=niche();row['assessment']['demand']['score']=float('nan')
        with self.assertRaises(ValueError):rank_niches({'niches':[row]})

    def test_duplicate_niche_ids_rejected(self):
        with self.assertRaises(ValueError):rank_niches({'niches':[niche(),niche()]})

    def test_keywords_separate_platform_period_and_provider_keep_missing(self):
        rows=[self.row(),self.row(keyword_ja='欠測',value=''),self.row(keyword_ja='高い',value='30'),
              self.row(platform='Google',value='90000'),self.row(period='2025-01'),self.row(provider='another')]
        result=keyword_report(self.csv(rows))
        self.assertEqual(len(result['groups']),4)
        values=result['groups'][0]['keywords']
        self.assertEqual([x['value'] for x in values],[30,10,None])
        self.assertEqual(values[0]['keyword_ja'],'高い')

    def test_unknown_volume_and_nonfinite_values_rejected(self):
        for row in [self.row(value='nan'),self.row(metric='unknown'),self.row(metric='relative_interest_index',value='101')]:
            with self.assertRaises(ValueError):keyword_report(self.csv([row]))

    def test_keyword_selection_rejects_wrong_market(self):
        self.choose()
        report=keyword_report(self.csv([self.row(market='US')]))
        write_json(self.root/'report.json',report)
        with self.assertRaises(ValueError):record_keyword(self.root,self.root/'report.json',0,'試験')

    def test_script_and_translation_bound_to_review(self):
        self.choose()
        with self.assertRaises(ValueError):prepare_speech(self.root,'voice')
        (self.root/'script.ja.txt').write_text('これは試験です。',encoding='utf-8')
        (self.root/'script.en.txt').write_text('This is a test.',encoding='utf-8')
        first=prepare_speech(self.root,'voice')
        self.assertIsNone(first['estimated_credits'])
        (self.root/'script.en.txt').write_text('Updated translation.',encoding='utf-8')
        second=prepare_speech(self.root,'voice')
        self.assertNotEqual(digest(first),digest(second))


class FakeYouTube:
    def __init__(self): self.calls=[]
    def get(self, endpoint, params):
        self.calls.append((endpoint,params))
        if endpoint=='search':
            return {'items':[{'id':{'videoId':'a'}},{'id':{'videoId':'b'}}]}
        return {'items':[{'id':i,'contentDetails':{'duration':d},
                         'snippet':{'title':'試験','channelId':'channel','channelTitle':'Fixture','publishedAt':'2026-01-01T00:00:00Z'},
                         'statistics':{'viewCount':'100'}} for i,d in [('a','PT45S'),('b','PT3M1S')]]}


class YouTubeTest(unittest.TestCase):
    def test_discovery_deduplicates_filters_duration_and_leaves_unknowns(self):
        api=FakeYouTube()
        data=discover(api,'試験',clock=datetime(2026,1,11,tzinfo=timezone.utc))
        self.assertEqual(len(api.calls),3)
        self.assertEqual(api.calls[-1][1]['id'],'a,b')
        self.assertEqual(len(data['candidates']),1)
        row=data['candidates'][0]
        self.assertIsNone(row['likes'])
        self.assertEqual(row['average_views_per_day'],10)
        self.assertEqual(shortlist(data)['by_total_views'],[])
        verify(data,'a','TEST ONLY: simulated inspection','Test title')
        self.assertEqual(len(shortlist(data)['by_total_views']),1)

    def test_duration_parser(self):
        self.assertEqual(seconds('PT1H2M3S'),3723)
        self.assertEqual(seconds('PT2M'),120)
        self.assertIsNone(seconds('garbage'))
        self.assertIsNone(seconds('PT'))

    def test_bounded_requests_and_unknown_id(self):
        with self.assertRaises(ValueError):discover(FakeYouTube(),'試験',pages=6)
        with self.assertRaises(ValueError):verify({'candidates':[]},'missing','Observed','Title')

    def test_pagination_is_bounded_even_when_more_results_exist(self):
        class Paged:
            def __init__(self):self.calls=[]
            def get(self,endpoint,params):
                self.calls.append(params)
                return {'items':[],'nextPageToken':'next'}
        api=Paged();discover(api,'試験',pages=2)
        self.assertEqual(len(api.calls),4)
        self.assertEqual(api.calls[1]['pageToken'],'next')

    def test_api_key_not_in_url(self):
        import io
        client=YouTube('secret-fixture')
        with patch.object(client.opener,'open',return_value=io.StringIO('{"items": []}')) as call:
            client.get('search',{'q':'試験'})
        request=call.call_args.args[0]
        self.assertNotIn('secret-fixture',request.full_url)
        self.assertEqual(request.get_header('X-goog-api-key'),'secret-fixture')


class JapaneseCaptionTest(unittest.TestCase):
    def test_unspaced_japanese_has_bounded_timed_cues(self):
        text='日本語の字幕を読みやすい長さに分けます。次の文章も正しく表示されます。'
        alignment={'characters':list(text),'character_start_times_seconds':[i*.15 for i in range(len(text))],
                   'character_end_times_seconds':[(i+1)*.15 for i in range(len(text))]}
        result=cues(alignment)
        self.assertGreater(len(result),2)
        self.assertEqual(''.join(x[0] for x in result),text)
        for content,start,end in result:
            self.assertLessEqual(len(content),18)
            self.assertLessEqual(end-start,3.00001)

    def test_nonmonotonic_ends_rejected(self):
        with self.assertRaises(ValueError):
            cues({'characters':['日','本'],'character_start_times_seconds':[0,.1],
                  'character_end_times_seconds':[1,.2]})


if __name__=='__main__': unittest.main()
