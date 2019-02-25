FROM gorialis/discord.py:3.7-rewrite-extras

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["./run-rpibot.sh"]
