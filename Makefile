init:
	pip3 install -r requirements.txt

clean:
	pystarter clean

run: clean
	gunicorn run:app --reload

stresstest: clean
	gunicorn run:app -w 6 --preload --max-requests-jitter 300
