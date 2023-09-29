from machine import Pin
from time import ticks_ms
from machine import PWM
from gpio_lcd import GpioLcd
from time import sleep
import umqtt_robust2 as mqtt

print('on')
##rotary code

pin_enc_a = 36 # skal muligvis byttes når vi har monteret studerendes rotary encoder
pin_enc_b = 39

rotenc_a = Pin(pin_enc_a, Pin.IN, Pin.PULL_UP)
rotenc_B = Pin(pin_enc_b, Pin.IN, Pin.PULL_UP)

# VARIABLES
enc_state = 0                               # Encoder state control variable

counter = 0

# Rotary encoder truth table, which one to use depends the actual rotary encoder hardware
encTableHalfStep = [
    [0x03, 0x02, 0x01, 0x00],
    [0x23, 0x00, 0x01, 0x00],
    [0x13, 0x02, 0x00, 0x00],
    [0x03, 0x05, 0x04, 0x00],
    [0x03, 0x03, 0x04, 0x10],
    [0x03, 0x05, 0x03, 0x20]]

encTableFullStep = [
    [0x00, 0x02, 0x04, 0x00],
    [0x03, 0x00, 0x01, 0x10],
    [0x03, 0x02, 0x00, 0x00],
    [0x03, 0x02, 0x01, 0x00],
    [0x06, 0x00, 0x04, 0x00],
    [0x06, 0x05, 0x00, 0x20],
    [0x06, 0x05, 0x04, 0x00]]


def re_half_step():
    global enc_state
    
    enc_state = encTableHalfStep[enc_state & 0x0F][(rotenc_B.value() << 1) | rotenc_a.value()]
 
    # -1: Left/CCW, 0: No rotation, 1: Right/CW
    result = enc_state & 0x30
    if (result == 0x10):
        return 1
    elif (result == 0x20):
        return -1
    else:
        return 0
#vores rotery encoder script

def re_full_step():
    global enc_state
    
    enc_state = encTableFullStep[enc_state & 0x0F][(rotenc_B.value() << 1) | rotenc_a.value()]
 
    # -1: Left/CCW, 0: No rotation, 1: Right/CW
    result = enc_state & 0x30
    if (result == 0x10):
        return 1
    elif (result == 0x20):
        return -1
    else:
        return 0

#laver vores lcd script
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32),
              d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

#lav begge vores pushbutens


pb1 = Pin(4, Pin.IN)
pb2 = Pin(0, Pin.IN)


#alle værdier der kommer til at blive brugt i resten af koden

rot_gng = 1
r = 0
pb1_pushed = 0
pb2_pushed = 0
#liste af alle beskeder du har modtaget
besked_liste = ['start af beskeder',]
#beskeden som du kommer til at skrive
txt = ''
#lav en tuppel med hele alpabeted i alpabetisk rækeflige plus mellemrum i enden
alpabet_list = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ')
user_name = ''
full_string = ''
response = ''

#txt pogram loop
def text_loop():
    while True:
        global r
        global rot_gng
        global alpabet_list
        global pb1_pushed
        global pb2_pushed
        global txt
        #set gør r støre med hver rotation
        r = r + re_full_step() # ændre r hvis der bliver drejet på roterry incodern
        #hvis r bliver for stor eller lille så den gå over idexet på tupelen set r til 0 for at ungå en fejl
        if r > 26 or r < -27:
            r = 0
        #hvis r er støre eller mindre end før
        if r != rot_gng:
            lcd.clear() #clear den siste besked fra lcdet 
            lcd.putstr(txt + alpabet_list[r]) #skriv den beske der er skrevet in til vider plus det neste bugstav i alpabetet efter valget før
            print(txt + alpabet_list[r]) # print i terminal for fejlfining 
            rot_gng = r 
            
        
        #pb1 debounse uden delay og set det nuværene tabugstav ind i txt
        if pb1.value() == 0 and pb1_pushed == 0:
            pb1_pushed = 1
            txt = txt + alpabet_list[r]
            r = 0
        elif pb1.value() == 0:
            ...
        else:
            pb1_pushed = 0
        
        #pb2 debounse uden delay og send txt til mqtt servern
        if pb2.value() == 0 and pb2_pushed == 0:
            pb2_pushed = 1
            mqtt.web_print(user_name+txt)
            txt = ''
            r = 0
            lcd.putstr(besked_liste[0]) #push den siste besked til lcdet
            break
            
        elif pb2.value() == 0:
            ...
        else:
            pb2_pushed = 0
        if mqtt.besked != besked_liste[0] and len(mqtt.besked) > 1 and mqtt.besked[0] != '#':
            besked_liste.insert(0,mqtt.besked)
        mqtt.sync_with_adafruitIO()

#engangs kode
mqtt.web_print('#/')
sleep(2.2)
for vænt in range (10):
    mqtt.sync_with_adafruitIO()
    if mqtt.besked[0:2] == '#&':
        print('fik et svar')
        full_list = mqtt.besked.split(',')
        besked_liste = full_list[1:]
        break
    sleep(0.3)
mqtt.web_print('#')

#vælg brugernavn
while True:
    r = r + re_full_step() # ændre r hvis der bliver drejet på roterry incodern
    #hvis r bliver for stor eller lille så den gå over idexet på tupelen set r til 0 for at ungå en fejl
    if r > 26 or r < -27:
        r = 0
    #hvis r er støre eller mindre end før
    if r != rot_gng:
        lcd.clear() #clear den siste besked fra lcdet
        lcd.putstr('skriv dit 2 bugstav brugernavn          ')
        lcd.putstr(txt + alpabet_list[r]) #skriv den beske der er skrevet in til vider plus det neste bugstav i alpabetet efter valget før
        print(txt + alpabet_list[r]) # print i terminal for fejlfining 
        rot_gng = r 
        
    
    #pb1 debounse uden delay og set det nuværene tabugstav ind i txt
    if pb1.value() == 0 and pb1_pushed == 0:
        pb1_pushed = 1
        txt = txt + alpabet_list[r]
        r = 0
    elif pb1.value() == 0:
        ...
    else:
        pb1_pushed = 0
    #sær for at bruernavnet ikke kan være over 2 bugstaver
    if len(txt) > 2:
        txt = ''
        lcd.clear() #clear den siste besked fra lcdet
        lcd.putstr('skriv dit 2 bugstav brugernavn          ')
        lcd.putstr(txt + alpabet_list[r]) #skriv den beske der er skrevet in til vider plus det neste bugstav i alpabetet efter valget før
    
    #sæt dit brugernavn
    if pb2.value() == 0 and pb2_pushed == 0 and len(txt) == 2:
        pb2_pushed = 1
        user_name = '['+txt+']'
        print(user_name)
        txt = ''
        r = 0
        lcd.clear()
        lcd.putstr(besked_liste[0]) #push den siste besked til lcdet
        break
        
    elif pb2.value() == 0:
        ...
    else:
        pb2_pushed = 0
    
    #chek om der er komet en ny besked og tilføj den til besked listen
    if mqtt.besked != besked_liste[0] and len(mqtt.besked) > 1 and mqtt.besked[0] != '#':
        besked_liste.insert(0,mqtt.besked)
    mqtt.sync_with_adafruitIO()

#main loop
while True:
    r = r + re_full_step() # ændre r hvis der bliver drejet på roterry incodern
    if r > len(besked_liste)-1 or r < 0: #hcid du drejer for langt vil den stoppe dig så der ikke komer en fejl
        r = 0
    if r != rot_gng:
        lcd.clear() #clear den siste besked fra lcdet 
        lcd.putstr(besked_liste[r]) #skriv den beske der er skrevet in til vider plus det neste bugstav i alpabetet efter valget før
        rot_gng = r
    
    if pb1.value() == 0 and pb1_pushed == 0:
        pb1_pushed = 1
        lcd.clear() #clear den siste besked fra lcdet
        lcd.putstr('a')#skriv a for at man kan se at man er i gang med at skrive en besked
        text_loop()#start med at skrive en besked
    elif pb1.value() == 0:
        ...
    else:
        pb1_pushed = 0
    
    if mqtt.besked != besked_liste[0] and len(mqtt.besked) > 1 and mqtt.besked[0] != '#':
        besked_liste.insert(0,mqtt.besked)#tilføj den siste besked til besked listen
        lcd.clear() #clear den siste besked fra lcdet 
        lcd.putstr(besked_liste[0]) #push den siste besked til lcdet
        print(besked_liste)
    
    if mqtt.besked[0:2] == '#/':
        for i in range (len(besked_liste)):
            full_string = full_string + ',' + besked_liste[i]
            if mqtt.besked[0:2] == '#&':
                full_string = ''
                break
        sleep(2.5)
        mqtt.web_print('#&'+full_string)
        full_string = ''
        
    
    mqtt.sync_with_adafruitIO()
    