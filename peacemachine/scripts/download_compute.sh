while true
do
	echo "downloading"
	rsync -avzh tensorflow-1-vm.us-west1-b.ml4p-1567995565833:/home/spenc/models /home/spenc/Dropbox/peace-machine/data/translation/ES
	echo "sleeping for 2 minutes"
	sleep 2m
done
