#!/usr/bin/env python3
"""Transcribe audio via Doubao Flash ASR. Loads ~/.agents/env then secrets."""
import base64, json, os, sys, uuid, urllib.request
from pathlib import Path

ENDPOINT = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
RESOURCE_ID = "volc.bigasr.auc_turbo"
SPEAKER_MAP = {"1": "speaker 1", "2": "speaker 2"}


def _load_secret_files() -> None:
    home = Path.home()
    for path in (
        home / ".agents" / "env" / "doubao-tts.env",
        home / ".agents" / "secrets" / "doubao-tts.env",
        home / ".hermes" / "secrets" / "doubao-tts.env",
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _auth_headers():
    _load_secret_files()
    api_key = (
        os.environ.get("DOUBAO_API_KEY")
        or os.environ.get("DOUBAO_SPEECH_API_KEY")
        or os.environ.get("DOUBAO_TTS2_API_KEY")
    )
    app_id = os.environ.get("DOUBAO_TTS_APP_ID")
    token = os.environ.get("DOUBAO_TTS_ACCESS_TOKEN")
    headers = {
        "Content-Type": "application/json",
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": str(uuid.uuid4()),
        "X-Api-Sequence": "-1",
    }
    if api_key:
        headers["X-Api-Key"] = api_key
        return headers, api_key
    if app_id and token:
        headers["X-Api-App-Key"] = app_id
        headers["X-Api-Access-Key"] = token
        return headers, app_id
    raise SystemExit("Missing Doubao credentials (DOUBAO_API_KEY in ~/.agents/env)")


def transcribe(audio_path, output_path):
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    print(f"Audio: {audio_path} ({len(audio_bytes)/1024/1024:.1f} MB)")
    headers, uid = _auth_headers()
    payload = {
        "user": {"uid": str(uid)[:64]},
        "audio": {"data": audio_b64},
        "request": {
            "model_name": "bigmodel",
            "enable_itn": True,
            "enable_punc": True,
            "enable_ddc": False,
            "enable_speaker_info": True,
            "show_utterances": True,
        },
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
    )
    print("Sending to Flash ASR...")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            status_code = resp.headers.get("X-Api-Status-Code", "")
            result = json.loads(resp.read())
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)
    if status_code != "20000000":
        print(f"API error: status={status_code}")
        print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}")
        sys.exit(1)
    utterances = result.get("result", {}).get("utterances", [])
    subtitles = []
    for utt in utterances:
        speaker_id = utt.get("additions", {}).get("speaker", "1")
        speaker_label = SPEAKER_MAP.get(speaker_id, f"speaker {speaker_id}")
        subtitles.append({
            "start": round(utt["start_time"] / 1000, 2),
            "end": round(utt["end_time"] / 1000, 2),
            "speaker": speaker_label,
            "text": utt["text"],
        })
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)
    txt_path = Path(output_path).with_suffix(".txt")
    txt_path.write_text("\n".join(s["text"] for s in subtitles), encoding="utf-8")
    print(f"Saved {len(subtitles)} utterances -> {output_path}")
    print(f"Plain text -> {txt_path}")
    return subtitles


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <audio.mp3> [output.json]")
        sys.exit(1)
    transcribe(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "transcript.json")
