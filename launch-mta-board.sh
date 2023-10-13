date=$(date '+%Y-%m-%d %H:%M:%S')
sudo python3 /home/dietpi/Repos/mta-board/mta-board.py &
echo "${date}: Started mta-board.py with PID ${!}" >> /home/dietpi/Repos/mta-board/mta-board.log
sudo python3 /home/dietpi/Repos/mta-board/mta-puller.py &
echo "${date}: Started mta-puller.py with PID ${!}" >> /home/dietpi/Repos/mta-board/mta-board.log
