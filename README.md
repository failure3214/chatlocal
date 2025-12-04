# python chat 

Small chat on python with local server and authorisation

# Files

server.py 
Local server (Can be used for online if using port forwarding)
Create sqlite database "chat.db" with two tables 

auth.py
authorisation
asks for ip (because i tested on my pc only)
has registration and login

chat.py 
base for chat 
you can read and type messages 
works like a group chat so everyone can see messages, new users receive a hustory of previous 20 messages 

auth.exe
combined auth.py and chat.py so no command lines appear because I didnt know how to remove them

# Usage
1. Start server.py
2. Use auth.py or auth.exe to start authorisation and chat
