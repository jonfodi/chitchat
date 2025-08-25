from google import genai
import dotenv

dotenv.load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message("I have 2 dogs in my house.")
print("*" * 50)
print("response 1")
print(response.text)
print("*" * 50)

print("*" * 50)
print("response 2")
response = chat.send_message("How many paws are in my house?")
print(response.text)
print("*" * 50)
for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)


