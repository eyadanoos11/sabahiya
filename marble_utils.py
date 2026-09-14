import numpy as np
from PIL import Image

def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = np.matrix(matrix, dtype=float)
    B = np.array(pb).reshape(8)
    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)

def apply_marble_perspective(uploaded_image_path, marble_image_path, points, output_path):
    # تحميل الصور
    kitchen = Image.open(uploaded_image_path).convert("RGB")
    marble = Image.open(marble_image_path).convert("RGB")
    
    # نقاط الزوايا الأربع من الصورة المحملة (المستخدم يحددها)
    # الترتيب: أعلى-يسار، أعلى-يمين، أسفل-يمين، أسفل-يسار
    pa = [(float(p[0]), float(p[1])) for p in points]
    
    # أبعاد صورة المطبخ
    w, h = kitchen.size
    
    # نقاط الزوايا الأربع لصورة الرخام (الخامة الأصلية)
    pb = [(0, 0), (marble.width, 0), (marble.width, marble.height), (0, marble.height)]
    
    # حساب معاملات التحويل
    coeffs = find_coeffs(pa, pb)
    
    # تحويل صورة الرخام لتطابق زوايا المطبخ
    warped_marble = marble.transform((w, h), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC)
    
    # دمج الصور: نقوم بوضع الرخام فوق المطبخ في المنطقة المحددة
    # نستخدم قناع (mask) لتحديد المنطقة (تعبئة النقاط الأربع باللون الأبيض)
    from PIL import ImageDraw
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon([tuple(p) for p in points], fill=255)
    
    # تركيب الرخام
    kitchen.paste(warped_marble, (0, 0), mask)
    
    # حفظ الصورة النهائية
    kitchen.save(output_path)
    return output_path
