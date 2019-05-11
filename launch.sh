#!/bin/bash
SESSION=$USER
OpenDaylight="~/Загрузки/karaf-0.8.4/"
OpenFlowApp="~/Загрузки/OpenDaylight-Openflow-App/"

tmux -2 new-session -d -s $SESSION

tmux new-window -t $SESSION:1 -n 'ODL'
tmux split-window -h 
tmux split-window -v 
tmux select-pane -t 0
tmux send-keys "cd $OpenDaylight/bin/" C-m
tmux send-keys "./karaf" C-m

tmux select-pane -t 1
tmux send-keys "sudo mn --controller=remote --topo=tree,3 --mac" C-m


tmux select-pane -t 2
tmux send-keys "cd $OpenFlowApp" C-m
tmux send-keys "grunt" C-m

tmux select-pane -t 0
tmux split-window -v 

tmux select-pane -t 2

tmux -2 attach-session -t $SESSION
