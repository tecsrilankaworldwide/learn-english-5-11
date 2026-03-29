from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import io
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ PHRASE DATA ============

LANGUAGES = [
    {"code": "ja", "name": "Japanese", "native_name": "日本語", "flag": "🇯🇵"},
    {"code": "ko", "name": "Korean", "native_name": "한국어", "flag": "🇰🇷"},
    {"code": "zh-TW", "name": "Taiwanese", "native_name": "台語", "flag": "🇹🇼"},
    {"code": "th", "name": "Thai", "native_name": "ไทย", "flag": "🇹🇭"},
    {"code": "vi", "name": "Vietnamese", "native_name": "Tiếng Việt", "flag": "🇻🇳"},
    {"code": "id", "name": "Indonesian", "native_name": "Bahasa Indonesia", "flag": "🇮🇩"},
    {"code": "zh-CN", "name": "Mandarin Chinese", "native_name": "普通话", "flag": "🇨🇳"},
    {"code": "zh-Hant", "name": "Traditional Chinese", "native_name": "繁體中文", "flag": "🇭🇰"},
    {"code": "yue", "name": "Cantonese", "native_name": "粵語", "flag": "🇭🇰"},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்", "flag": "🇮🇳"},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "flag": "🇮🇳"},
    {"code": "si", "name": "Sinhala", "native_name": "සිංහල", "flag": "🇱🇰"},
    {"code": "ur", "name": "Urdu", "native_name": "اردو", "flag": "🇵🇰"},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "flag": "🇧🇩"},
]

CATEGORIES = [
    {"id": "greetings", "name": "Greetings", "icon": "HandWaving"},
    {"id": "shopping", "name": "Shopping", "icon": "ShoppingCart"},
    {"id": "food", "name": "Food & Dining", "icon": "ForkKnife"},
    {"id": "directions", "name": "Directions", "icon": "MapPin"},
    {"id": "emergency", "name": "Emergency", "icon": "FirstAid"},
    {"id": "social", "name": "Social", "icon": "ChatCircle"},
    {"id": "transport", "name": "Transportation", "icon": "Car"},
    {"id": "accommodation", "name": "Accommodation", "icon": "Bed"},
]

# Phrase translations for all languages
PHRASES_DATA = {
    "greetings": [
        {
            "english": "Hello",
            "translations": {
                "ja": "こんにちは", "ko": "안녕하세요", "zh-TW": "你好", "th": "สวัสดี",
                "vi": "Xin chào", "id": "Halo", "zh-CN": "你好", "zh-Hant": "你好",
                "yue": "你好", "ta": "வணக்கம்", "hi": "नमस्ते", "si": "ආයුබෝවන්",
                "ur": "السلام علیکم", "bn": "নমস্কার"
            }
        },
        {
            "english": "Good morning",
            "translations": {
                "ja": "おはようございます", "ko": "좋은 아침이에요", "zh-TW": "早安", "th": "สวัสดีตอนเช้า",
                "vi": "Chào buổi sáng", "id": "Selamat pagi", "zh-CN": "早上好", "zh-Hant": "早安",
                "yue": "早晨", "ta": "காலை வணக்கம்", "hi": "शुभ प्रभात", "si": "සුභ උදෑසනක්",
                "ur": "صبح بخیر", "bn": "সুপ্রভাত"
            }
        },
        {
            "english": "Good evening",
            "translations": {
                "ja": "こんばんは", "ko": "좋은 저녁이에요", "zh-TW": "晚安", "th": "สวัสดีตอนเย็น",
                "vi": "Chào buổi tối", "id": "Selamat malam", "zh-CN": "晚上好", "zh-Hant": "晚安",
                "yue": "晚安", "ta": "மாலை வணக்கம்", "hi": "शुभ संध्या", "si": "සුභ සන්ධ්‍යාවක්",
                "ur": "شام بخیر", "bn": "শুভ সন্ধ্যা"
            }
        },
        {
            "english": "How are you?",
            "translations": {
                "ja": "お元気ですか？", "ko": "잘 지내세요?", "zh-TW": "你好嗎？", "th": "คุณสบายดีไหม?",
                "vi": "Bạn khỏe không?", "id": "Apa kabar?", "zh-CN": "你好吗？", "zh-Hant": "你好嗎？",
                "yue": "你好嗎？", "ta": "நலமா?", "hi": "आप कैसे हैं?", "si": "ඔබට කෙසේද?",
                "ur": "آپ کیسے ہیں؟", "bn": "আপনি কেমন আছেন?"
            }
        },
        {
            "english": "Thank you",
            "translations": {
                "ja": "ありがとうございます", "ko": "감사합니다", "zh-TW": "謝謝", "th": "ขอบคุณ",
                "vi": "Cảm ơn", "id": "Terima kasih", "zh-CN": "谢谢", "zh-Hant": "謝謝",
                "yue": "多謝", "ta": "நன்றி", "hi": "धन्यवाद", "si": "ස්තූතියි",
                "ur": "شکریہ", "bn": "ধন্যবাদ"
            }
        },
        {
            "english": "You're welcome",
            "translations": {
                "ja": "どういたしまして", "ko": "천만에요", "zh-TW": "不客氣", "th": "ยินดี",
                "vi": "Không có gì", "id": "Sama-sama", "zh-CN": "不客气", "zh-Hant": "不客氣",
                "yue": "唔使客氣", "ta": "பரவாயில்லை", "hi": "कोई बात नहीं", "si": "සාදරයෙන් පිළිගනිමු",
                "ur": "کوئی بات نہیں", "bn": "স্বাগতম"
            }
        },
        {
            "english": "Goodbye",
            "translations": {
                "ja": "さようなら", "ko": "안녕히 가세요", "zh-TW": "再見", "th": "ลาก่อน",
                "vi": "Tạm biệt", "id": "Selamat tinggal", "zh-CN": "再见", "zh-Hant": "再見",
                "yue": "再見", "ta": "பிரியாவிடை", "hi": "अलविदा", "si": "ආයුබෝවන්",
                "ur": "خدا حافظ", "bn": "বিদায়"
            }
        },
        {
            "english": "Nice to meet you",
            "translations": {
                "ja": "はじめまして", "ko": "만나서 반갑습니다", "zh-TW": "很高興認識你", "th": "ยินดีที่ได้รู้จัก",
                "vi": "Rất vui được gặp bạn", "id": "Senang bertemu dengan Anda", "zh-CN": "很高兴认识你", "zh-Hant": "很高興認識你",
                "yue": "好高興認識你", "ta": "உங்களை சந்தித்ததில் மகிழ்ச்சி", "hi": "आपसे मिलकर खुशी हुई", "si": "ඔබව හමුවීම සතුටක්",
                "ur": "آپ سے مل کر خوشی ہوئی", "bn": "আপনার সাথে দেখা করে ভালো লাগলো"
            }
        },
    ],
    "shopping": [
        {
            "english": "How much is this?",
            "translations": {
                "ja": "これはいくらですか？", "ko": "이것은 얼마예요?", "zh-TW": "這個多少錢？", "th": "อันนี้ราคาเท่าไหร่?",
                "vi": "Cái này bao nhiêu tiền?", "id": "Berapa harganya?", "zh-CN": "这个多少钱？", "zh-Hant": "這個多少錢？",
                "yue": "呢個幾錢？", "ta": "இது எவ்வளவு?", "hi": "यह कितने का है?", "si": "මෙය කීයද?",
                "ur": "یہ کتنے کا ہے؟", "bn": "এটার দাম কত?"
            }
        },
        {
            "english": "Can I pay by card?",
            "translations": {
                "ja": "カードで払えますか？", "ko": "카드로 결제할 수 있나요?", "zh-TW": "可以刷卡嗎？", "th": "จ่ายด้วยบัตรได้ไหม?",
                "vi": "Tôi có thể thanh toán bằng thẻ không?", "id": "Bisa bayar pakai kartu?", "zh-CN": "可以刷卡吗？", "zh-Hant": "可以刷卡嗎？",
                "yue": "可唔可以碌卡？", "ta": "கார்டு மூலம் செலுத்த முடியுமா?", "hi": "क्या मैं कार्ड से भुगतान कर सकता हूं?", "si": "කාඩ් එකෙන් ගෙවන්න පුළුවන්ද?",
                "ur": "کیا میں کارڈ سے ادائیگی کر سکتا ہوں؟", "bn": "আমি কি কার্ড দিয়ে পেমেন্ট করতে পারি?"
            }
        },
        {
            "english": "Do you have a smaller size?",
            "translations": {
                "ja": "小さいサイズはありますか？", "ko": "더 작은 사이즈 있어요?", "zh-TW": "有小一點的尺寸嗎？", "th": "มีไซส์เล็กกว่านี้ไหม?",
                "vi": "Có size nhỏ hơn không?", "id": "Ada ukuran yang lebih kecil?", "zh-CN": "有小一点的尺寸吗？", "zh-Hant": "有小一點的尺寸嗎？",
                "yue": "有冇細碼？", "ta": "சிறிய அளவு இருக்கிறதா?", "hi": "क्या छोटा साइज है?", "si": "කුඩා ප්‍රමාණයක් තිබේද?",
                "ur": "کیا چھوٹا سائز ہے؟", "bn": "ছোট সাইজ আছে?"
            }
        },
        {
            "english": "Can I try this on?",
            "translations": {
                "ja": "試着してもいいですか？", "ko": "입어봐도 될까요?", "zh-TW": "我可以試穿嗎？", "th": "ลองใส่ได้ไหม?",
                "vi": "Tôi có thể thử cái này không?", "id": "Boleh saya coba ini?", "zh-CN": "我可以试穿吗？", "zh-Hant": "我可以試穿嗎？",
                "yue": "可唔可以試吓？", "ta": "இதை அணிந்து பார்க்கலாமா?", "hi": "क्या मैं इसे पहनकर देख सकता हूं?", "si": "මට මේක ඇඳලා බලන්න පුළුවන්ද?",
                "ur": "کیا میں اسے پہن کر دیکھ سکتا ہوں؟", "bn": "আমি কি এটা পরে দেখতে পারি?"
            }
        },
        {
            "english": "It's too expensive",
            "translations": {
                "ja": "高すぎます", "ko": "너무 비싸요", "zh-TW": "太貴了", "th": "แพงไป",
                "vi": "Đắt quá", "id": "Terlalu mahal", "zh-CN": "太贵了", "zh-Hant": "太貴了",
                "yue": "太貴啦", "ta": "மிகவும் விலை அதிகம்", "hi": "यह बहुत महंगा है", "si": "එය ඉතා මිල අධිකයි",
                "ur": "یہ بہت مہنگا ہے", "bn": "এটা অনেক দামি"
            }
        },
        {
            "english": "Can you give me a discount?",
            "translations": {
                "ja": "値引きしてもらえますか？", "ko": "할인해 주실 수 있나요?", "zh-TW": "可以便宜一點嗎？", "th": "ลดราคาได้ไหม?",
                "vi": "Bạn có thể giảm giá không?", "id": "Bisa kasih diskon?", "zh-CN": "可以便宜一点吗？", "zh-Hant": "可以便宜一點嗎？",
                "yue": "可唔可以平啲？", "ta": "தள்ளுபடி தருவீர்களா?", "hi": "क्या आप छूट दे सकते हैं?", "si": "ඔබට මට වට්ටමක් දිය හැකිද?",
                "ur": "کیا آپ رعایت دے سکتے ہیں؟", "bn": "আপনি কি ছাড় দিতে পারবেন?"
            }
        },
        {
            "english": "I'll take it",
            "translations": {
                "ja": "これをください", "ko": "이거 살게요", "zh-TW": "我要這個", "th": "เอาอันนี้",
                "vi": "Tôi sẽ mua cái này", "id": "Saya ambil ini", "zh-CN": "我要这个", "zh-Hant": "我要這個",
                "yue": "我要呢個", "ta": "இதை எடுத்துக்கொள்கிறேன்", "hi": "मुझे यह चाहिए", "si": "මම මේක ගන්නම්",
                "ur": "میں یہ لے لوں گا", "bn": "আমি এটা নেব"
            }
        },
        {
            "english": "Where is the fitting room?",
            "translations": {
                "ja": "試着室はどこですか？", "ko": "탈의실이 어디예요?", "zh-TW": "試衣間在哪裡？", "th": "ห้องลองเสื้ออยู่ที่ไหน?",
                "vi": "Phòng thử đồ ở đâu?", "id": "Kamar pas di mana?", "zh-CN": "试衣间在哪里？", "zh-Hant": "試衣間在哪裡？",
                "yue": "試身室喺邊度？", "ta": "டிரையல் ரூம் எங்கே?", "hi": "ट्रायल रूम कहां है?", "si": "ඇඳුම් කාමරය කොහිද?",
                "ur": "ٹرائل روم کہاں ہے؟", "bn": "ট্রায়াল রুম কোথায়?"
            }
        },
    ],
    "food": [
        {
            "english": "Where can I eat good and hygienic food?",
            "translations": {
                "ja": "衛生的で美味しい食事ができる場所はどこですか？", "ko": "위생적이고 맛있는 음식은 어디서 먹을 수 있나요?", "zh-TW": "哪裡可以吃到乾淨衛生的食物？", "th": "ที่ไหนกินอาหารสะอาดและอร่อยได้บ้าง?",
                "vi": "Tôi có thể ăn ở đâu có đồ ăn ngon và sạch sẽ?", "id": "Di mana saya bisa makan makanan yang enak dan higienis?", "zh-CN": "哪里可以吃到干净卫生的食物？", "zh-Hant": "哪裡可以吃到乾淨衛生的食物？",
                "yue": "邊度有乾淨好食嘅嘢食？", "ta": "நல்ல சுத்தமான உணவு எங்கே கிடைக்கும்?", "hi": "अच्छा और स्वच्छ खाना कहां मिलेगा?", "si": "හොඳ සනීපාරක්ෂක ආහාර කොහෙන් කන්න පුළුවන්ද?",
                "ur": "صاف ستھرا اور اچھا کھانا کہاں مل سکتا ہے؟", "bn": "ভালো এবং পরিচ্ছন্ন খাবার কোথায় পাব?"
            }
        },
        {
            "english": "Can I have a coffee with you?",
            "translations": {
                "ja": "一緒にコーヒーを飲みませんか？", "ko": "같이 커피 마실래요?", "zh-TW": "我可以和你一起喝杯咖啡嗎？", "th": "ไปดื่มกาแฟด้วยกันไหม?",
                "vi": "Tôi có thể uống cà phê với bạn không?", "id": "Boleh saya minum kopi dengan Anda?", "zh-CN": "我可以和你一起喝杯咖啡吗？", "zh-Hant": "我可以和你一起喝杯咖啡嗎？",
                "yue": "可唔可以同你飲杯咖啡？", "ta": "உங்களுடன் காபி குடிக்கலாமா?", "hi": "क्या मैं आपके साथ कॉफी पी सकता हूं?", "si": "ඔබ සමඟ කෝපි එකක් බොන්න පුළුවන්ද?",
                "ur": "کیا میں آپ کے ساتھ کافی پی سکتا ہوں؟", "bn": "আমি কি আপনার সাথে কফি খেতে পারি?"
            }
        },
        {
            "english": "I am vegetarian",
            "translations": {
                "ja": "私はベジタリアンです", "ko": "저는 채식주의자입니다", "zh-TW": "我吃素", "th": "ฉันกินมังสวิรัติ",
                "vi": "Tôi ăn chay", "id": "Saya vegetarian", "zh-CN": "我吃素", "zh-Hant": "我吃素",
                "yue": "我食齋", "ta": "நான் சைவம் சாப்பிடுவேன்", "hi": "मैं शाकाहारी हूं", "si": "මම නිර්මාංශකයෙක්",
                "ur": "میں سبزی خور ہوں", "bn": "আমি নিরামিষভোজী"
            }
        },
        {
            "english": "I am allergic to nuts",
            "translations": {
                "ja": "ナッツアレルギーがあります", "ko": "견과류 알레르기가 있어요", "zh-TW": "我對堅果過敏", "th": "ฉันแพ้ถั่ว",
                "vi": "Tôi bị dị ứng với các loại hạt", "id": "Saya alergi kacang", "zh-CN": "我对坚果过敏", "zh-Hant": "我對堅果過敏",
                "yue": "我對果仁敏感", "ta": "எனக்கு கொட்டைகள் ஒவ்வாமை", "hi": "मुझे मेवों से एलर्जी है", "si": "මට රට කජු වලට අසාත්මිකතාවයක් ඇත",
                "ur": "مجھے خشک میوے سے الرجی ہے", "bn": "আমার বাদামে অ্যালার্জি আছে"
            }
        },
        {
            "english": "Can I see the menu?",
            "translations": {
                "ja": "メニューを見せてください", "ko": "메뉴판 좀 볼 수 있을까요?", "zh-TW": "可以看菜單嗎？", "th": "ขอดูเมนูได้ไหม?",
                "vi": "Cho tôi xem thực đơn được không?", "id": "Boleh lihat menunya?", "zh-CN": "可以看菜单吗？", "zh-Hant": "可以看菜單嗎？",
                "yue": "可唔可以睇吓餐牌？", "ta": "மெனு பார்க்கலாமா?", "hi": "क्या मैं मेन्यू देख सकता हूं?", "si": "මට menu එක බලන්න පුළුවන්ද?",
                "ur": "کیا میں مینو دیکھ سکتا ہوں؟", "bn": "আমি কি মেনু দেখতে পারি?"
            }
        },
        {
            "english": "The bill please",
            "translations": {
                "ja": "お会計お願いします", "ko": "계산서 주세요", "zh-TW": "請結帳", "th": "เก็บเงินด้วยค่ะ",
                "vi": "Cho tôi hóa đơn", "id": "Minta bill nya", "zh-CN": "请结账", "zh-Hant": "請結帳",
                "yue": "埋單唔該", "ta": "பில் கொடுங்கள்", "hi": "बिल दे दीजिए", "si": "බිල් එක දෙන්න",
                "ur": "بل دے دیں", "bn": "বিল দিন"
            }
        },
        {
            "english": "This is delicious",
            "translations": {
                "ja": "とてもおいしいです", "ko": "정말 맛있어요", "zh-TW": "這很好吃", "th": "อร่อยมาก",
                "vi": "Món này ngon quá", "id": "Ini enak sekali", "zh-CN": "这很好吃", "zh-Hant": "這很好吃",
                "yue": "好好食", "ta": "இது சுவையாக இருக்கிறது", "hi": "यह बहुत स्वादिष्ट है", "si": "මේක හරිම රසයි",
                "ur": "یہ بہت مزیدار ہے", "bn": "এটা অনেক সুস্বাদু"
            }
        },
        {
            "english": "Can I have water please?",
            "translations": {
                "ja": "お水をください", "ko": "물 주세요", "zh-TW": "請給我水", "th": "ขอน้ำหน่อยค่ะ",
                "vi": "Cho tôi nước nhé", "id": "Minta air ya", "zh-CN": "请给我水", "zh-Hant": "請給我水",
                "yue": "唔該俾杯水", "ta": "தண்ணீர் தருவீர்களா?", "hi": "कृपया पानी दे दीजिए", "si": "කරුණාකර වතුර දෙන්න",
                "ur": "پانی دے دیں", "bn": "একটু পানি দেবেন?"
            }
        },
    ],
    "directions": [
        {
            "english": "Where is the washroom?",
            "translations": {
                "ja": "トイレはどこですか？", "ko": "화장실이 어디예요?", "zh-TW": "洗手間在哪裡？", "th": "ห้องน้ำอยู่ที่ไหน?",
                "vi": "Nhà vệ sinh ở đâu?", "id": "Toilet di mana?", "zh-CN": "洗手间在哪里？", "zh-Hant": "洗手間在哪裡？",
                "yue": "廁所喺邊度？", "ta": "கழிவறை எங்கே?", "hi": "शौचालय कहां है?", "si": "නාන කාමරය කොහිද?",
                "ur": "واش روم کہاں ہے؟", "bn": "টয়লেট কোথায়?"
            }
        },
        {
            "english": "How do I get to the train station?",
            "translations": {
                "ja": "駅へはどう行けばいいですか？", "ko": "기차역에 어떻게 가나요?", "zh-TW": "火車站怎麼走？", "th": "ไปสถานีรถไฟยังไง?",
                "vi": "Đến ga tàu bằng cách nào?", "id": "Bagaimana cara ke stasiun kereta?", "zh-CN": "火车站怎么走？", "zh-Hant": "火車站怎麼走？",
                "yue": "點樣去火車站？", "ta": "ரயில் நிலையம் எப்படி போவது?", "hi": "रेलवे स्टेशन कैसे जाऊं?", "si": "දුම්රිය ස්ථානයට යන්නේ කොහොමද?",
                "ur": "ریلوے اسٹیشن کیسے جاؤں؟", "bn": "ট্রেন স্টেশনে কিভাবে যাব?"
            }
        },
        {
            "english": "Is it far from here?",
            "translations": {
                "ja": "ここから遠いですか？", "ko": "여기서 멀어요?", "zh-TW": "離這裡遠嗎？", "th": "ไกลจากที่นี่ไหม?",
                "vi": "Có xa đây không?", "id": "Apakah jauh dari sini?", "zh-CN": "离这里远吗？", "zh-Hant": "離這裡遠嗎？",
                "yue": "離呢度遠唔遠？", "ta": "இங்கிருந்து தூரமா?", "hi": "क्या यहां से दूर है?", "si": "මෙතනින් දුරද?",
                "ur": "کیا یہاں سے دور ہے؟", "bn": "এখান থেকে কি দূরে?"
            }
        },
        {
            "english": "Turn left/right",
            "translations": {
                "ja": "左/右に曲がってください", "ko": "왼쪽/오른쪽으로 가세요", "zh-TW": "左轉/右轉", "th": "เลี้ยวซ้าย/ขวา",
                "vi": "Rẽ trái/phải", "id": "Belok kiri/kanan", "zh-CN": "左转/右转", "zh-Hant": "左轉/右轉",
                "yue": "轉左/右", "ta": "இடது/வலது திரும்பு", "hi": "बाएं/दाएं मुड़िए", "si": "වමට/දකුණට හැරෙන්න",
                "ur": "بائیں/دائیں مڑیں", "bn": "বামে/ডানে ঘুরুন"
            }
        },
        {
            "english": "Go straight",
            "translations": {
                "ja": "まっすぐ行ってください", "ko": "직진하세요", "zh-TW": "直走", "th": "ตรงไป",
                "vi": "Đi thẳng", "id": "Jalan lurus", "zh-CN": "直走", "zh-Hant": "直走",
                "yue": "直行", "ta": "நேராக போங்க", "hi": "सीधे जाइए", "si": "කෙලින් යන්න",
                "ur": "سیدھے جائیں", "bn": "সোজা যান"
            }
        },
        {
            "english": "Can you show me on the map?",
            "translations": {
                "ja": "地図で教えてもらえますか？", "ko": "지도에서 보여주실 수 있어요?", "zh-TW": "可以在地圖上指給我看嗎？", "th": "ช่วยชี้บนแผนที่ให้หน่อยได้ไหม?",
                "vi": "Bạn có thể chỉ trên bản đồ được không?", "id": "Bisa tunjukkan di peta?", "zh-CN": "可以在地图上指给我看吗？", "zh-Hant": "可以在地圖上指給我看嗎？",
                "yue": "可唔可以喺地圖度指俾我睇？", "ta": "வரைபடத்தில் காட்ட முடியுமா?", "hi": "क्या आप मुझे मैप पर दिखा सकते हैं?", "si": "map එකේ පෙන්නන්න පුළුවන්ද?",
                "ur": "کیا آپ نقشے پر دکھا سکتے ہیں؟", "bn": "আপনি কি ম্যাপে দেখাতে পারবেন?"
            }
        },
        {
            "english": "I am lost",
            "translations": {
                "ja": "道に迷いました", "ko": "길을 잃었어요", "zh-TW": "我迷路了", "th": "ฉันหลงทาง",
                "vi": "Tôi bị lạc", "id": "Saya tersesat", "zh-CN": "我迷路了", "zh-Hant": "我迷路了",
                "yue": "我蕩失路", "ta": "நான் வழி தவறிவிட்டேன்", "hi": "मैं रास्ता भटक गया", "si": "මම මග හැරුණා",
                "ur": "میں راستہ بھول گیا", "bn": "আমি পথ হারিয়ে ফেলেছি"
            }
        },
    ],
    "emergency": [
        {
            "english": "Help!",
            "translations": {
                "ja": "助けて！", "ko": "도와주세요!", "zh-TW": "救命！", "th": "ช่วยด้วย!",
                "vi": "Cứu tôi với!", "id": "Tolong!", "zh-CN": "救命！", "zh-Hant": "救命！",
                "yue": "救命！", "ta": "உதவி!", "hi": "मदद!", "si": "උදව් කරන්න!",
                "ur": "مدد!", "bn": "সাহায্য করুন!"
            }
        },
        {
            "english": "I need a doctor",
            "translations": {
                "ja": "医者が必要です", "ko": "의사가 필요해요", "zh-TW": "我需要看醫生", "th": "ฉันต้องการหมอ",
                "vi": "Tôi cần bác sĩ", "id": "Saya butuh dokter", "zh-CN": "我需要看医生", "zh-Hant": "我需要看醫生",
                "yue": "我要睇醫生", "ta": "எனக்கு மருத்துவர் வேண்டும்", "hi": "मुझे डॉक्टर चाहिए", "si": "මට වෛද්‍යවරයෙක් අවශ්‍යයි",
                "ur": "مجھے ڈاکٹر چاہیے", "bn": "আমার ডাক্তার দরকার"
            }
        },
        {
            "english": "Call the police",
            "translations": {
                "ja": "警察を呼んでください", "ko": "경찰을 불러주세요", "zh-TW": "請叫警察", "th": "โทรเรียกตำรวจ",
                "vi": "Gọi cảnh sát", "id": "Panggil polisi", "zh-CN": "请叫警察", "zh-Hant": "請叫警察",
                "yue": "報警", "ta": "போலீஸை அழைக்கவும்", "hi": "पुलिस को बुलाओ", "si": "පොලිසියට කතා කරන්න",
                "ur": "پولیس کو بلاؤ", "bn": "পুলিশ ডাকুন"
            }
        },
        {
            "english": "I lost my passport",
            "translations": {
                "ja": "パスポートをなくしました", "ko": "여권을 잃어버렸어요", "zh-TW": "我的護照丟了", "th": "ฉันทำพาสปอร์ตหาย",
                "vi": "Tôi bị mất hộ chiếu", "id": "Saya kehilangan paspor", "zh-CN": "我的护照丢了", "zh-Hant": "我的護照丟了",
                "yue": "我唔見咗護照", "ta": "என் பாஸ்போர்ட் தொலைந்துவிட்டது", "hi": "मेरा पासपोर्ट खो गया", "si": "මගේ passport එක නැතිවුණා",
                "ur": "میرا پاسپورٹ کھو گیا", "bn": "আমার পাসপোর্ট হারিয়ে গেছে"
            }
        },
        {
            "english": "I don't feel well",
            "translations": {
                "ja": "気分が悪いです", "ko": "몸이 안 좋아요", "zh-TW": "我不舒服", "th": "ฉันไม่สบาย",
                "vi": "Tôi không khỏe", "id": "Saya tidak enak badan", "zh-CN": "我不舒服", "zh-Hant": "我不舒服",
                "yue": "我唔舒服", "ta": "எனக்கு உடம்பு சரியில்லை", "hi": "मेरी तबीयत ठीक नहीं है", "si": "මට සනීප නැහැ",
                "ur": "میری طبیعت ٹھیک نہیں", "bn": "আমার শরীর ভালো লাগছে না"
            }
        },
        {
            "english": "Where is the hospital?",
            "translations": {
                "ja": "病院はどこですか？", "ko": "병원이 어디예요?", "zh-TW": "醫院在哪裡？", "th": "โรงพยาบาลอยู่ที่ไหน?",
                "vi": "Bệnh viện ở đâu?", "id": "Rumah sakit di mana?", "zh-CN": "医院在哪里？", "zh-Hant": "醫院在哪裡？",
                "yue": "醫院喺邊度？", "ta": "மருத்துவமனை எங்கே?", "hi": "अस्पताल कहां है?", "si": "රෝහල කොහිද?",
                "ur": "ہسپتال کہاں ہے؟", "bn": "হাসপাতাল কোথায়?"
            }
        },
    ],
    "social": [
        {
            "english": "I like your style",
            "translations": {
                "ja": "あなたのスタイルが好きです", "ko": "당신의 스타일이 좋아요", "zh-TW": "我喜歡你的風格", "th": "ฉันชอบสไตล์ของคุณ",
                "vi": "Tôi thích phong cách của bạn", "id": "Saya suka gaya Anda", "zh-CN": "我喜欢你的风格", "zh-Hant": "我喜歡你的風格",
                "yue": "我鍾意你嘅風格", "ta": "உங்கள் ஸ்டைல் எனக்குப் பிடிக்கும்", "hi": "मुझे आपका स्टाइल पसंद है", "si": "මට ඔබේ style එක ආසයි",
                "ur": "مجھے آپ کا انداز پسند ہے", "bn": "আমি আপনার স্টাইল পছন্দ করি"
            }
        },
        {
            "english": "What is your father doing?",
            "translations": {
                "ja": "お父さんは何をしていますか？", "ko": "아버지는 무슨 일을 하세요?", "zh-TW": "你爸爸做什麼工作？", "th": "พ่อของคุณทำงานอะไร?",
                "vi": "Bố bạn làm nghề gì?", "id": "Ayah Anda kerja apa?", "zh-CN": "你爸爸做什么工作？", "zh-Hant": "你爸爸做什麼工作？",
                "yue": "你老豆做咩架？", "ta": "உங்கள் தந்தை என்ன செய்கிறார்?", "hi": "आपके पिताजी क्या करते हैं?", "si": "ඔබගේ තාත්තා මොකද කරන්නේ?",
                "ur": "آپ کے والد کیا کرتے ہیں؟", "bn": "আপনার বাবা কি করেন?"
            }
        },
        {
            "english": "Can we be friends?",
            "translations": {
                "ja": "友達になれますか？", "ko": "우리 친구가 될 수 있을까요?", "zh-TW": "我們可以做朋友嗎？", "th": "เราเป็นเพื่อนกันได้ไหม?",
                "vi": "Chúng ta có thể làm bạn không?", "id": "Boleh kita berteman?", "zh-CN": "我们可以做朋友吗？", "zh-Hant": "我們可以做朋友嗎？",
                "yue": "我哋可唔可以做朋友？", "ta": "நாம் நண்பர்களாக முடியுமா?", "hi": "क्या हम दोस्त बन सकते हैं?", "si": "අපිට මිතුරන් වෙන්න පුළුවන්ද?",
                "ur": "کیا ہم دوست بن سکتے ہیں؟", "bn": "আমরা কি বন্ধু হতে পারি?"
            }
        },
        {
            "english": "What is your name?",
            "translations": {
                "ja": "お名前は何ですか？", "ko": "이름이 뭐예요?", "zh-TW": "你叫什麼名字？", "th": "คุณชื่ออะไร?",
                "vi": "Bạn tên gì?", "id": "Siapa nama Anda?", "zh-CN": "你叫什么名字？", "zh-Hant": "你叫什麼名字？",
                "yue": "你叫咩名？", "ta": "உங்கள் பெயர் என்ன?", "hi": "आपका नाम क्या है?", "si": "ඔබගේ නම මොකක්ද?",
                "ur": "آپ کا نام کیا ہے؟", "bn": "আপনার নাম কি?"
            }
        },
        {
            "english": "Where are you from?",
            "translations": {
                "ja": "どちらから来ましたか？", "ko": "어디에서 오셨어요?", "zh-TW": "你從哪裡來？", "th": "คุณมาจากที่ไหน?",
                "vi": "Bạn đến từ đâu?", "id": "Anda berasal dari mana?", "zh-CN": "你从哪里来？", "zh-Hant": "你從哪裡來？",
                "yue": "你係邊度嚟？", "ta": "நீங்கள் எங்கிருந்து வருகிறீர்கள்?", "hi": "आप कहां से हैं?", "si": "ඔබ කොහෙන්ද ආවේ?",
                "ur": "آپ کہاں سے ہیں؟", "bn": "আপনি কোথা থেকে এসেছেন?"
            }
        },
        {
            "english": "Do you speak English?",
            "translations": {
                "ja": "英語を話せますか？", "ko": "영어 할 줄 아세요?", "zh-TW": "你會說英語嗎？", "th": "คุณพูดภาษาอังกฤษได้ไหม?",
                "vi": "Bạn nói tiếng Anh được không?", "id": "Anda bisa berbahasa Inggris?", "zh-CN": "你会说英语吗？", "zh-Hant": "你會說英語嗎？",
                "yue": "你識唔識講英文？", "ta": "நீங்கள் ஆங்கிலம் பேசுவீர்களா?", "hi": "क्या आप अंग्रेज़ी बोलते हैं?", "si": "ඔබ ඉංග්‍රීසි කතා කරනවාද?",
                "ur": "کیا آپ انگریزی بولتے ہیں؟", "bn": "আপনি কি ইংরেজি বলতে পারেন?"
            }
        },
    ],
    "transport": [
        {
            "english": "How much is the taxi fare?",
            "translations": {
                "ja": "タクシー代はいくらですか？", "ko": "택시 요금이 얼마예요?", "zh-TW": "計程車費多少？", "th": "ค่าแท็กซี่เท่าไหร่?",
                "vi": "Giá taxi bao nhiêu?", "id": "Berapa ongkos taksinya?", "zh-CN": "出租车费多少？", "zh-Hant": "計程車費多少？",
                "yue": "的士收幾錢？", "ta": "டாக்சி கட்டணம் என்ன?", "hi": "टैक्सी का किराया कितना है?", "si": "ටැක්සි ගාස්තුව කීයද?",
                "ur": "ٹیکسی کا کرایہ کتنا ہے؟", "bn": "ট্যাক্সি ভাড়া কত?"
            }
        },
        {
            "english": "Please take me to the airport",
            "translations": {
                "ja": "空港まで行ってください", "ko": "공항까지 가 주세요", "zh-TW": "請載我去機場", "th": "ไปสนามบินหน่อย",
                "vi": "Làm ơn đưa tôi đến sân bay", "id": "Tolong antar saya ke bandara", "zh-CN": "请载我去机场", "zh-Hant": "請載我去機場",
                "yue": "唔該載我去機場", "ta": "என்னை விமான நிலையத்திற்கு அழைத்துச் செல்லுங்கள்", "hi": "कृपया मुझे एयरपोर्ट ले जाइए", "si": "කරුණාකර මාව ගුවන් තොටුපලට ගෙනියන්න",
                "ur": "براہ کرم مجھے ایئرپورٹ لے جائیں", "bn": "আমাকে এয়ারপোর্টে নিয়ে যান"
            }
        },
        {
            "english": "Where can I buy a ticket?",
            "translations": {
                "ja": "チケットはどこで買えますか？", "ko": "표는 어디서 살 수 있어요?", "zh-TW": "在哪裡買票？", "th": "ซื้อตั๋วได้ที่ไหน?",
                "vi": "Tôi có thể mua vé ở đâu?", "id": "Di mana saya bisa beli tiket?", "zh-CN": "在哪里买票？", "zh-Hant": "在哪裡買票？",
                "yue": "喺邊度買飛？", "ta": "டிக்கெட் எங்கே வாங்கலாம்?", "hi": "टिकट कहां मिलेगा?", "si": "ටිකට් එක කොහෙන් ගන්නද?",
                "ur": "ٹکٹ کہاں سے ملے گا؟", "bn": "টিকিট কোথায় কিনব?"
            }
        },
        {
            "english": "Is this the right bus?",
            "translations": {
                "ja": "このバスで合っていますか？", "ko": "이 버스가 맞나요?", "zh-TW": "這是對的公車嗎？", "th": "นี่รถเมล์สายที่ถูกต้องไหม?",
                "vi": "Đây có phải xe buýt đúng không?", "id": "Apakah ini bus yang benar?", "zh-CN": "这是对的公交车吗？", "zh-Hant": "這是對的公車嗎？",
                "yue": "呢架係唔係啱巴士？", "ta": "இது சரியான பஸ் தானா?", "hi": "क्या यह सही बस है?", "si": "මේක හරි බස් එකද?",
                "ur": "کیا یہ صحیح بس ہے؟", "bn": "এটা কি সঠিক বাস?"
            }
        },
        {
            "english": "When does the next train leave?",
            "translations": {
                "ja": "次の電車は何時ですか？", "ko": "다음 기차는 언제 출발해요?", "zh-TW": "下一班火車幾點開？", "th": "รถไฟขบวนต่อไปออกกี่โมง?",
                "vi": "Chuyến tàu tiếp theo mấy giờ?", "id": "Kapan kereta berikutnya berangkat?", "zh-CN": "下一班火车几点开？", "zh-Hant": "下一班火車幾點開？",
                "yue": "下班火車幾點開？", "ta": "அடுத்த ரயில் எப்போது புறப்படும்?", "hi": "अगली ट्रेन कब छूटेगी?", "si": "ඊළඟ දුම්රිය කීයට යනවද?",
                "ur": "اگلی ٹرین کب روانہ ہوگی؟", "bn": "পরের ট্রেন কখন ছাড়বে?"
            }
        },
        {
            "english": "Stop here please",
            "translations": {
                "ja": "ここで止まってください", "ko": "여기서 세워주세요", "zh-TW": "請在這裡停車", "th": "จอดตรงนี้ค่ะ",
                "vi": "Dừng ở đây nhé", "id": "Tolong berhenti di sini", "zh-CN": "请在这里停车", "zh-Hant": "請在這裡停車",
                "yue": "唔該喺度停車", "ta": "இங்கே நிறுத்துங்கள்", "hi": "कृपया यहां रुकिए", "si": "කරුණාකර මෙතන නවත්වන්න",
                "ur": "یہاں رکیں", "bn": "এখানে থামুন"
            }
        },
    ],
    "accommodation": [
        {
            "english": "I have a reservation",
            "translations": {
                "ja": "予約があります", "ko": "예약이 있어요", "zh-TW": "我有訂房", "th": "ฉันจองไว้แล้ว",
                "vi": "Tôi có đặt phòng trước", "id": "Saya punya reservasi", "zh-CN": "我有预订", "zh-Hant": "我有訂房",
                "yue": "我有訂房", "ta": "நான் முன்பதிவு செய்துள்ளேன்", "hi": "मेरी बुकिंग है", "si": "මට වෙන් කිරීමක් තියනවා",
                "ur": "میرا بکنگ ہے", "bn": "আমার বুকিং আছে"
            }
        },
        {
            "english": "Is breakfast included?",
            "translations": {
                "ja": "朝食は含まれていますか？", "ko": "조식 포함인가요?", "zh-TW": "有包含早餐嗎？", "th": "รวมอาหารเช้าไหม?",
                "vi": "Có bao gồm bữa sáng không?", "id": "Apakah termasuk sarapan?", "zh-CN": "包含早餐吗？", "zh-Hant": "有包含早餐嗎？",
                "yue": "包唔包早餐？", "ta": "காலை உணவு சேர்க்கப்பட்டுள்ளதா?", "hi": "क्या नाश्ता शामिल है?", "si": "උදෑසන ආහාරය ඇතුළත්ද?",
                "ur": "کیا ناشتہ شامل ہے؟", "bn": "সকালের নাস্তা অন্তর্ভুক্ত আছে?"
            }
        },
        {
            "english": "Can I see the room first?",
            "translations": {
                "ja": "部屋を先に見てもいいですか？", "ko": "방을 먼저 볼 수 있을까요?", "zh-TW": "可以先看房間嗎？", "th": "ขอดูห้องก่อนได้ไหม?",
                "vi": "Tôi có thể xem phòng trước không?", "id": "Boleh lihat kamarnya dulu?", "zh-CN": "可以先看房间吗？", "zh-Hant": "可以先看房間嗎？",
                "yue": "可唔可以先睇吓間房？", "ta": "முதலில் அறையைப் பார்க்கலாமா?", "hi": "क्या मैं पहले कमरा देख सकता हूं?", "si": "මුලින්ම කාමරය බලන්න පුළුවන්ද?",
                "ur": "کیا میں پہلے کمرا دیکھ سکتا ہوں؟", "bn": "আমি কি আগে রুম দেখতে পারি?"
            }
        },
        {
            "english": "What time is checkout?",
            "translations": {
                "ja": "チェックアウトは何時ですか？", "ko": "체크아웃 시간이 언제예요?", "zh-TW": "退房時間是幾點？", "th": "เช็คเอาท์กี่โมง?",
                "vi": "Mấy giờ trả phòng?", "id": "Jam berapa checkout?", "zh-CN": "退房时间是几点？", "zh-Hant": "退房時間是幾點？",
                "yue": "幾點checkout？", "ta": "செக்அவுட் நேரம் என்ன?", "hi": "चेकआउट का समय क्या है?", "si": "checkout වෙලාව කීයද?",
                "ur": "چیک آؤٹ کا وقت کیا ہے؟", "bn": "চেকআউট কখন?"
            }
        },
        {
            "english": "Is there WiFi?",
            "translations": {
                "ja": "WiFiはありますか？", "ko": "와이파이 있어요?", "zh-TW": "有WiFi嗎？", "th": "มี WiFi ไหม?",
                "vi": "Có WiFi không?", "id": "Ada WiFi?", "zh-CN": "有WiFi吗？", "zh-Hant": "有WiFi嗎？",
                "yue": "有冇WiFi？", "ta": "WiFi இருக்கிறதா?", "hi": "क्या WiFi है?", "si": "WiFi තියනවද?",
                "ur": "WiFi ہے؟", "bn": "WiFi আছে?"
            }
        },
        {
            "english": "The air conditioning is not working",
            "translations": {
                "ja": "エアコンが動きません", "ko": "에어컨이 안 돼요", "zh-TW": "冷氣壞了", "th": "แอร์ไม่ทำงาน",
                "vi": "Máy lạnh không hoạt động", "id": "AC-nya tidak berfungsi", "zh-CN": "空调坏了", "zh-Hant": "冷氣壞了",
                "yue": "冷氣壞咗", "ta": "ஏசி வேலை செய்யவில்லை", "hi": "AC काम नहीं कर रहा", "si": "AC එක වැඩ කරන්නේ නැහැ",
                "ur": "AC کام نہیں کر رہا", "bn": "AC কাজ করছে না"
            }
        },
    ],
}


# ============ MODELS ============

class TTSRequest(BaseModel):
    text: str
    language_code: str = "en"


# ============ ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "Travel Phrase Companion API"}


@api_router.get("/languages")
async def get_languages():
    """Get all supported languages"""
    return {"languages": LANGUAGES}


@api_router.get("/categories")
async def get_categories():
    """Get all phrase categories"""
    return {"categories": CATEGORIES}


@api_router.get("/phrases/{category_id}")
async def get_phrases_by_category(category_id: str, language_code: str = "ja"):
    """Get phrases for a specific category and language"""
    if category_id not in PHRASES_DATA:
        raise HTTPException(status_code=404, detail="Category not found")
    
    phrases = PHRASES_DATA[category_id]
    result = []
    
    for phrase in phrases:
        translation = phrase["translations"].get(language_code, "")
        result.append({
            "id": str(uuid.uuid4()),
            "english": phrase["english"],
            "native": translation,
            "language_code": language_code
        })
    
    return {"phrases": result, "category": category_id}


@api_router.get("/phrases")
async def get_all_phrases(language_code: str = "ja"):
    """Get all phrases for a language"""
    all_phrases = []
    
    for category_id, phrases in PHRASES_DATA.items():
        for phrase in phrases:
            translation = phrase["translations"].get(language_code, "")
            all_phrases.append({
                "id": str(uuid.uuid4()),
                "category": category_id,
                "english": phrase["english"],
                "native": translation,
                "language_code": language_code
            })
    
    return {"phrases": all_phrases}


@api_router.post("/tts/generate")
async def generate_tts(request: TTSRequest):
    """Generate text-to-speech audio using OpenAI TTS"""
    try:
        from emergentintegrations.llm.openai import OpenAITextToSpeech
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="TTS API key not configured")
        
        tts = OpenAITextToSpeech(api_key=api_key)
        
        # Generate speech
        audio_base64 = await tts.generate_speech_base64(
            text=request.text,
            model="tts-1",
            voice="nova",
            speed=0.9  # Slightly slower for learning
        )
        
        return {
            "audio_base64": audio_base64,
            "format": "mp3",
            "text": request.text
        }
        
    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@api_router.post("/tts/stream")
async def stream_tts(request: TTSRequest):
    """Stream TTS audio as binary response"""
    try:
        from emergentintegrations.llm.openai import OpenAITextToSpeech
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="TTS API key not configured")
        
        tts = OpenAITextToSpeech(api_key=api_key)
        
        # Generate speech
        audio_bytes = await tts.generate_speech(
            text=request.text,
            model="tts-1",
            voice="nova",
            speed=0.9
        )
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except Exception as e:
        logger.error(f"TTS streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS streaming failed: {str(e)}")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
