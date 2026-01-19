import pyopenjtalk
import pyworld as pw
import numpy as np
import soundfile as sf
text = "イントネーションを調整します"

# 音声生成（素の音声）
x, sr = pyopenjtalk.tts(text)

# WORLDで解析
_f0, t = pw.dio(x.astype(np.float64), sr)
f0 = pw.stonemask(x.astype(np.float64), _f0, t, sr)
sp = pw.cheaptrick(x.astype(np.float64), f0, t, sr)
ap = pw.d4c(x.astype(np.float64), f0, t, sr)

# アクセント操作（例：全体を少し高く）
f0 *= 1.2

# 再合成
y = pw.synthesize(f0, sp, ap, sr)

# 保存
sf.write("output.wav", y, sr)
