import smtplib, ssl
from email.message import EmailMessage
from smtplib import SMTP, SMTPException, SMTPAuthenticationError, SMTPConnectError, SMTPServerDisconnected, SMTPSenderRefused, SMTPHeloError
from getpass import getpass
TO = input("To: ")
FROM = input("From: ")
# Manual settings input by user
rotori = input("Rotor 1 setting? (Enter a roman numeral from I to V):\n")
rotorii = input("Rotor 2 setting? (Enter a roman numeral from I to V):\n")
rotoriii = input("Rotor 3 setting? (Enter a roman numeral from I to V):\n")
ringsettingi = input("Ring settings? (Enter a combination of three capital letters:\n")
ringpositioni = input("Ring position? (Enter a combination of three capital letters):\n")
# ----------------- Settings ------------------------
rotors = (rotori.upper(),rotorii.upper(),rotoriii.upper())
reflector = "UKW-B" # Choose between UKW-B and UKW-C
ringSettings = ringsettingi.upper() #Choose any three letters
ringPositions = ringpositioni.upper() # Choose any three letters
plugboard = "AT BS DE FM IR KN LZ OW PV XY" # not too much of a need to change this but whatever makes ya happy!
# ---------------------------------------------------

# Behind the curtain...
def caesarShift(str, amount):
	output = ""

	for i in range(0,len(str)):
		c = str[i]
		code = ord(c)
		if ((code >= 65) and (code <= 90)):
			c = chr(((code - 65 + amount) % 26) + 65)
		output = output + c
	
	return output

def encode(plaintext):
  global rotors, reflector,ringSettings,ringPositions,plugboard
  #Rotors and reflectors
  rotor1 = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
  rotor1Notch = "Q"
  rotor2 = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
  rotor2Notch = "E"
  rotor3 = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
  rotor3Notch = "V"
  rotor4 = "ESOVPZJAYQUIRHXLNFTGKDCMWB"
  rotor4Notch = "J"
  rotor5 = "VZBRGITYUPSDNHLXAWMJQOFECK"
  rotor5Notch = "Z" 
  
  rotorDict = {"I":rotor1,"II":rotor2,"III":rotor3,"IV":rotor4,"V":rotor5}
  rotorNotchDict = {"I":rotor1Notch,"II":rotor2Notch,"III":rotor3Notch,"IV":rotor4Notch,"V":rotor5Notch}  
  
  reflectorB = {"A":"Y","Y":"A","B":"R","R":"B","C":"U","U":"C","D":"H","H":"D","E":"Q","Q":"E","F":"S","S":"F","G":"L","L":"G","I":"P","P":"I","J":"X","X":"J","K":"N","N":"K","M":"O","O":"M","T":"Z","Z":"T","V":"W","W":"V"}
  reflectorC = {"A":"F","F":"A","B":"V","V":"B","C":"P","P":"C","D":"J","J":"D","E":"I","I":"E","G":"O","O":"G","H":"Y","Y":"H","K":"R","R":"K","L":"Z","Z":"L","M":"X","X":"M","N":"W","W":"N","Q":"T","T":"Q","S":"U","U":"S"}
  
  alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  rotorANotch = False
  rotorBNotch = False
  rotorCNotch = False
  
  if reflector=="UKW-B":
    reflectorDict = reflectorB
  else:
    reflectorDict = reflectorC
  
  #A = Left,  B = Mid,  C= Right 
  rotorA = rotorDict[rotors[0]]
  rotorB = rotorDict[rotors[1]]
  rotorC = rotorDict[rotors[2]]
  rotorANotch = rotorNotchDict[rotors[0]]
  rotorBNotch = rotorNotchDict[rotors[1]]
  rotorCNotch = rotorNotchDict[rotors[2]]
  
  rotorALetter = ringPositions[0]
  rotorBLetter = ringPositions[1]
  rotorCLetter = ringPositions[2]
  
  rotorASetting = ringSettings[0]
  offsetASetting = alphabet.index(rotorASetting)
  rotorBSetting = ringSettings[1]
  offsetBSetting = alphabet.index(rotorBSetting)
  rotorCSetting = ringSettings[2]
  offsetCSetting = alphabet.index(rotorCSetting)
  
  rotorA = caesarShift(rotorA,offsetASetting)
  rotorB = caesarShift(rotorB,offsetBSetting)
  rotorC = caesarShift(rotorC,offsetCSetting)
  
  if offsetASetting>0:
    rotorA = rotorA[26-offsetASetting:] + rotorA[0:26-offsetASetting]
  if offsetBSetting>0:
    rotorB = rotorB[26-offsetBSetting:] + rotorB[0:26-offsetBSetting]
  if offsetCSetting>0:
    rotorC = rotorC[26-offsetCSetting:] + rotorC[0:26-offsetCSetting]

  ciphertext = ""
  
  #put Conver plugboard settings into a dictionary
  plugboardConnections = plugboard.upper().split(" ")
  plugboardDict = {}
  for pair in plugboardConnections:
    if len(pair)==2:
      plugboardDict[pair[0]] = pair[1]
      plugboardDict[pair[1]] = pair[0]
  
  plaintext = plaintext.upper()  
  for letter in plaintext:
    encryptedLetter = letter  
    
    if letter in alphabet:
      #Rotate Rotors - This happens as soon as a key is pressed
      rotorTrigger = False
      #Third rotor rotates by 1 for every key being pressed
      if rotorCLetter == rotorCNotch:
        rotorTrigger = True 
      rotorCLetter = alphabet[(alphabet.index(rotorCLetter) + 1) % 26]
      #Check if rotorB needs to rotate
      if rotorTrigger:
        rotorTrigger = False
        if rotorBLetter == rotorBNotch:
          rotorTrigger = True 
        rotorBLetter = alphabet[(alphabet.index(rotorBLetter) + 1) % 26]
  
        #Check if rotorA needs to rotate
        if (rotorTrigger):
          rotorTrigger = False
          rotorALetter = alphabet[(alphabet.index(rotorALetter) + 1) % 26]
      		 
      else:
          #Checks for double step sequence
        if rotorBLetter == rotorBNotch:
          rotorBLetter = alphabet[(alphabet.index(rotorBLetter) + 1) % 26]
          rotorALetter = alphabet[(alphabet.index(rotorALetter) + 1) % 26]
        
      #Plugboard encryption
      if letter in plugboardDict.keys():
        if plugboardDict[letter]!="":
          encryptedLetter = plugboardDict[letter]
    
      #Rotors and Reflector Encryption
      offsetA = alphabet.index(rotorALetter)
      offsetB = alphabet.index(rotorBLetter)
      offsetC = alphabet.index(rotorCLetter)

      # Wheel 3 Encryption
      pos = alphabet.index(encryptedLetter)
      let = rotorC[(pos + offsetC)%26]
      pos = alphabet.index(let)
      encryptedLetter = alphabet[(pos - offsetC +26)%26]
      
      # Wheel 2 Encryption
      pos = alphabet.index(encryptedLetter)
      let = rotorB[(pos + offsetB)%26]
      pos = alphabet.index(let)
      encryptedLetter = alphabet[(pos - offsetB +26)%26]
      
      # Wheel 1 Encryption
      pos = alphabet.index(encryptedLetter)
      let = rotorA[(pos + offsetA)%26]
      pos = alphabet.index(let)
      encryptedLetter = alphabet[(pos - offsetA +26)%26]
      
      # Reflector encryption!
      if encryptedLetter in reflectorDict.keys():
        if reflectorDict[encryptedLetter]!="":
          encryptedLetter = reflectorDict[encryptedLetter]
      
      #Back through the rotors 
      # Wheel 1 Encryption
      pos = alphabet.index(encryptedLetter)
      let = alphabet[(pos + offsetA)%26]
      pos = rotorA.index(let)
      encryptedLetter = alphabet[(pos - offsetA +26)%26] 
      
      # Wheel 2 Encryption
      pos = alphabet.index(encryptedLetter)
      let = alphabet[(pos + offsetB)%26]
      pos = rotorB.index(let)
      encryptedLetter = alphabet[(pos - offsetB +26)%26]
      
      # Wheel 3 Encryption
      pos = alphabet.index(encryptedLetter)
      let = alphabet[(pos + offsetC)%26]
      pos = rotorC.index(let)
      encryptedLetter = alphabet[(pos - offsetC +26)%26]
      
      #Implement plugboard encryption!
      if encryptedLetter in plugboardDict.keys():
        if plugboardDict[encryptedLetter]!="":
          encryptedLetter = plugboardDict[encryptedLetter]

    ciphertext = ciphertext + encryptedLetter
  
  return ciphertext# Manual settings input by user
plaintext = input("Enter body of email\n")
ciphertext = encode(plaintext)
message = ciphertext
port = 465  # For SSL
serveri = input("Mail Server? (ex. smtp.gmail.com for gmail): ")
password = getpass("Password: ")

# Create a secure SSL context
context = ssl.create_default_context()
try: 
  with smtplib.SMTP_SSL(serveri, port, context=context) as server:
    server.login(FROM, password)
    server.sendmail(FROM, TO, message)
    print("email sent successfully")
    server.quit()
# Error Handling. See Readme for further explanation
except SMTPAuthenticationError:
    print("AUTHENTICATION ERROR: Possible causes: \n Incorrect username/password \n Security settings prohibit access. (example: make sure <less secure app access> is enabled for gmail users)")
except SMTPConnectError:
    print("ERROR: Unable to connect to SMTP server. The server may be down, or you entered it incorrectly. ")
except SMTPServerDisconnected:
    print("ERROR: SMTP Server disconnected unexpectedly")
except SMTPSenderRefused:
    print("ERROR: Sender address refused by server")
except SMTPHeloError:
    print("ERROR: SMTP server refused HELO/EHLO message")
print("press ENTER to close the program")
input()