import hashlib

class CryptoChallenge:
    id = "crypto"
    title = "Stack Overflow"
    category = "CRYPTO"
    difficulty = "Intermediate"

    FLAG_HASH = "200e45667be46ae234c53e0756b2459dd457e810c0cb07355614b66fa317c232"
    EASTER_EGG = "> Encryption reversed. Feelings remain encrypted."

    CIPHERTEXT = (
        "1RwG7add0ehBe2mjzOKKcHhJJ9sp4ehWOQCoMnQ8ET7LdY9EClt6WXdR6ws6OEetyZQm"
        "OJRysrp2JhZkBzMZQbMH1tlF578bdE4r0Lj0kuqyY0CmP6kYSAe1nXW0tTGwKerOnjM3"
        "Q8clmThbf0wbeSHDK8IpMw18haUAYxCOUbVzbx8qWT"
    )

    scenario = """
    Signals intelligence intercepted an encrypted transmission routed through multiple nested relays.
    
    Field analysts noted that the payload was transformed in successive stages across different eras of cryptography:
    - The outer envelope is packed into a compact alphanumeric string using digits and mixed-case letters.
    - Beneath the surface lies an ubiquitous binary-to-text encoding standard common in web and mail protocols.
    - At the core, the message is locked with a classical rotational cipher from antiquity.

    Peel back the layers step-by-step from outside to inside to recover the plaintext and find the flag!
    """

    hints = [
        "The message is layered from the outside in. Inspect the character set of the outer envelope: digits, lowercase, and uppercase symbols combined suggest a 62-character radix.",
        "Unpacking the outer radix representation yields ASCII text formatted for standard web data encoding.",
        "Once the digital encodings are stripped, the underlying text is shifted by a fixed key. Look for familiar English letter frequencies or test small Caesar shifts."
    ]

    @classmethod
    def check_flag(cls, flag_input: str) -> bool:
        if not flag_input:
            return False
        clean = flag_input.strip()
        h = hashlib.sha256(clean.encode('utf-8')).hexdigest()
        return h == cls.FLAG_HASH

