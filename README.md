# AMERICAN WEDDING

> A romantic Capture The Flag (CTF) web application disguised as a cybersecurity challenge, culminating in a proposal reveal with a 3D ASCII diamond ring animation video.

---

## Challenges Overview

1. **SANITY — "Sanity Check" (Moderate)**
   - Terminal access handshake requiring the secret shared keyphrase.
   - Hint: `"our minecraft world"`
   - Flag: `CTF{ladybug}` (or `ladybug`, case-insensitive).

2. **PWN — "Holy C" (Moderate/Hard)**
   - Classic x86-64 stack buffer overflow with `gets()` and ret2win control hijacking.
   - Provides vulnerable source code (`vuln.c`) and downloadable compiled Linux binary.
   - Flag: `CTF{buffer_overflow_unlocked}`
   - Solve proof: `python tools/solve_binary.py`

3. **CRYPTO — "Stack Overflow" (Moderate/Hard)**
   - 3-layer cipher cascade: Plaintext $\rightarrow$ Caesar (+3) $\rightarrow$ Base64 $\rightarrow$ Base62.
   - Unpacking Base62 using big-endian integer reconstruction with alphanumeric alphabet `0-9A-Za-z`.
   - Flag: `CTF{triple_layer_decoded}`
   - Build & verification tool: `python tools/build_crypto.py`

4. **OSINT — "The Lost Monument" (Moderate)**
   - Classified field intelligence dossier referencing a 17th-century riverbank mausoleum built for love.
   - Forgiving normalization accepting `CTF{taj_mahal}`, `taj mahal`, or case-insensitive variants.
   - Flag: `CTF{taj_mahal}`

5. **STEGO / CRYPTO — "Insanity Check" (Hard)**
   - Terminal log with hidden/invisible payload appended at the end of the text.
   - Invisible on screen via CSS (`opacity: 0`, transparent font), but revealed when copied and pasted into external applications (Notepad, VS Code, CyberChef).
   - The trailing hidden text is encrypted using an Affine Cipher ($a = 7$, $b = 10$).
   - Flag: `CTF{affine_insanity_conquered}`

6. **FINAL REVEAL — "System Override"**
   - Triggers once all 5 flags are captured.
   - Interactive terminal loading sequence (`Compiling feelings... Initialising Heart.exe...`).
   - Plays a high-resolution 3D procedural ASCII diamond ring video in a glowing rose gold frame.
   - Prompts with `[ YES ]` button, transitioning to `STATUS: HAPPILY COMPROMISED`.

---

## 🚀 Quickstart

### 1. Local Run
Install dependencies and launch Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### 2. Fast-Forward / Dev Mode
To instantly test or demo the final proposal sequence without manually solving the challenges:

- **Via environment variable**:
  ```bash
  # Windows PowerShell
  $env:DEV_SKIP="1"; streamlit run app.py

  # Linux / macOS
  DEV_SKIP=1 streamlit run app.py
  ```
- **Via browser URL parameter**:
  Append `?dev=1` to the URL:
  `http://localhost:8501/?dev=1`

- **Via in-app button**:
  Click "RESET PROTOCOL SESSION" at the bottom of Mission Control to reset anytime.

---

## 🐳 Running the Binary Challenge (Docker)

Because the PWN challenge target is a Linux ELF binary, players on Windows or macOS can build and debug it in the included Docker environment:

```bash
# Build the Docker image
docker build -t american-wedding-pwn .

# Run an interactive shell in the container
docker run -it --rm american-wedding-pwn

# Inside container: run the binary or solver
./vuln
python3 /challenge/solve_binary.py
```

To compile the binary locally on Linux:
```bash
bash tools/build_binary.sh
```

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your repository.
3. Set the Main file path to `app.py`.
4. Deploy! All challenge logic, flag verifications (via SHA-256 hashes), and 3D ASCII rendering run entirely in pure Python without requiring any OS-specific external libraries.

---

## 📁 Repository Layout

```
american-wedding/
├── app.py                  # UI, routing, state, final reveal
├── challenges/
│   ├── __init__.py         # Challenge registry
│   ├── binary.py           # PWN challenge metadata & SHA-256 check
│   ├── crypto.py           # CRYPTO challenge metadata & SHA-256 check
│   └── osint.py            # OSINT challenge metadata & SHA-256 check
├── renderer.py             # Thin wrapper around 3D ASCII ring engine with caching
├── tools/
│   ├── build_crypto.py     # Generates & verifies ciphertext
│   ├── build_binary.sh     # Compiles the vulnerable C program
│   └── solve_binary.py     # Proof-of-solve exploit script
├── assets/
│   ├── binary/             # vuln.c and compiled binary
│   └── ring/               # Untouched 3D ASCII procedural ring engine
├── Dockerfile              # Container environment for PWN challenge
├── requirements.txt        # Dependencies (streamlit, numpy)
└── README.md
```

