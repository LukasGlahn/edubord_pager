# https://rfzero.net/tutorials/rotary-encoder/

from machine import Pin
from time import ticks_ms
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
       
       
#print("Rotary encoder test program\n")
def rotary_encoder_tester():
    global counter
    testing = True
    print("Tester rotary encoder, drej så tallet kommer under -10")
    left = False
    right = False
    start = ticks_ms()
    while testing:
        # Read the rotary encoder
        res = re_full_step()                    
        if ticks_ms() - start > 15000:
            print("Stopper rotary encoder test - 15 sekunder er gået")
            rotary_timeout_svar = input("Vil du prøve at teste rotary encoder igen? ja/nej")
            if rotary_timeout_svar == "ja":
                rotary_timeout_svar == ""
                return rotary_encoder_tester()
            else:
                return "Rotary encoder virker ikke - tid gået"
        # Direction and counter
        counter += res
        if counter < -9 and left == False:
            print("Ok, drej nu til tallet er over 10")
            left = True
        if counter > 10 and left == True:
            print("👍 Rotary encoder virker")
            testing = False
            return "👍 Rotary encoder virker"
        if (res == 1):
            print("Right/CW: %d" % counter)
        elif (res == -1):
            print("Left/CCW: %d" % counter)
#rotary_encoder_tester()