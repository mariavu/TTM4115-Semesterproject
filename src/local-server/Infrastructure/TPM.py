#Trusted Platform Module Mock
class TPM:
    def validateToken(self, token):
        return True 
 # In reality, the real life TPM module will use actual public keys to verify the authenticity/integrity of the token