# Issue and verify a handoff

Run from the host repository. Set PROJECT to the private project path. Set BRIEF to research-brief.json's path **relative to that project**. Use the actual skill installation path if it is installed in a user directory. The following example uses a project installation.

~~~sh
HANDOFF=.claude/skills/research-next-video/scripts/handoff.py
python "$HANDOFF" writer "$PROJECT" "$BRIEF"
python "$HANDOFF" editor "$PROJECT" "$BRIEF" --script script.ja.txt
python "$HANDOFF" verify "$PROJECT" "$BRIEF"
~~~

Run the first command after the coordinator has signed off on the evidence. Send its output path and the project path to the assigned writer. Ask for the actual script file, factual sources, and a rule ID to excerpt mapping. Verify those artifacts. Only then run the second command with the real new script. Send that packet and project path to the video editor. It binds the exact script bytes. Request the actual storyboard and rule ID to shot mapping before accepting the response. Paths inside packets are project-relative.

Run the third command after the editor returns and again before the host's production gate. A changed topic evidence file, learning revision, packet or script invalidates the check. If the script is revised, issue the editor a fresh packet, obtain a reconciled shot list and update the host's application receipt. A research refresh requires rebuilding the brief and reissuing dependent assignments. Preserve earlier runs.

If the editor has no paired script and frame observations, hold that stage and identify the missing videos or permissions. A writer may still prepare an original script with valid spoken evidence. A worker's structured reply should state the run ID, packet path, output path(s), rule applications and unresolved evidence. The coordinator verifies the files before calling a task complete. A prepared packet alone is not a delivery acknowledgement.
