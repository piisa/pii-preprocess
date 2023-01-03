"""
Test the reading plain text files in different languages
"""

from pathlib import Path

import pii_preprocess.doc.text.load as mod


DATADIR = Path(__file__).parents[2] / "data" / "text" / "lang"


# ----------------------------------------------------------------


def test200_paragraphs_zh():
    """
    Split by paragraphs, chinese text
    """
    opt = {"mode": "para"}
    obj = mod.TextSrcDocument(DATADIR / "zh-yangtze.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 53
    assert got[1].data == "== 名称 ==\n\n\n"


def test201_paragraphs_zh_eos():
    """
    Split by paragraphs, chinese text, split also by sentence & newlines
    """
    opt = {"mode": "para", "eos": True}
    obj = mod.TextSrcDocument(DATADIR / "zh-yangtze.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 86
    assert got[1].data == "長江和黄河並稱爲中华文化的母親河，孕育了長江文明和黄河文明。2019年，长江三角洲经济区约占中国GDP的24%，人口规模达到2.27亿。长江流域生态类型多样，水生生物资源丰富，是多种濒危动物如扬子鳄和达氏鲟的栖息地。几千年来，人们利用长江取水、灌溉、排污、运输、发展工业、当作边界等。\n"


def test210_paragraphs_ar():
    """
    Split by paragraphs, arabic text
    """
    opt = {"mode": "para"}
    obj = mod.TextSrcDocument(DATADIR / "ar-indian-ocean.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 22
    assert got[1].data == "== جغرافيا ==\n\n"


def test211_paragraphs_ar_eos():
    """
    Split by paragraphs, arabic text, eos
    """
    opt = {"mode": "para", "eos": True}
    obj = mod.TextSrcDocument(DATADIR / "ar-indian-ocean.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 47
    assert got[1].data == "يقدر حجم المحيط 292.131.000 كيلومتر مكعب (70.086.000 ميل مكعب). جزر صغيرة منتشرة في الحافات القارية. الجزيرة الأم في المحيط هي جزيرة مدغشقر، رابع أكبر جزيرة؛ جزيرة ريونيون، جزر القمر، سيشيل، جزر المالديف، موريشيوس، وسري لانكا. ويعد أرخبيل أندونيسيا هي حدود المحيط في الشرق.\n\n\n"


def test220_paragraphs_hi():
    """
    Split by paragraphs, hindi text
    """
    opt = {"mode": "para"}
    obj = mod.TextSrcDocument(DATADIR / "hi-indian-ocean.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 16
    assert got[0].data == """हिन्द महासागर दुनिया का तीसरा सबसे बड़ा समुद्र है और पृथ्वी की सतह पर उपस्थित पानी का लगभग 20% भाग इसमें समाहित है। उत्तर में यह भारतीय उपमहाद्वीप से, पश्चिम में पूर्व अफ्रीका; पूर्व में हिन्दचीन, सुंदा द्वीप समूह और ऑस्ट्रेलिया, तथा दक्षिण में दक्षिणध्रुवीय महासागर से घिरा है। विश्व में केवल यही एक महासागर है जिसका नाम किसी देश के नाम यानी, हिन्दुस्तान (भारत) के नाम है। प्राचीन भारतीय ग्रंथो में इसे "रत्नाकर" कहा गया है।
वैश्विक रूप से परस्पर जुड़े समुद्रों के एक घटक हिंद महासागर को, अटलांटिक महासागर से 20° पूर्व देशांतर जो केप एगुलस से गुजरती है और प्रशांत महासागर से 146°55' पूर्व देशांतर पृथक करती हैं। हिंद महासागर की उत्तरी सीमा का निर्धारण फारस की खाड़ी में 30° उत्तर अक्षांश द्वारा होता है। हिंद महासागर की पृष्टधाराओं का परिसंचरण असममित है। अफ्रीका और ऑस्ट्रेलिया के दक्षिणी सिरों पर इस महासागर की चौड़ाई करीब 10,000 किलोमीटर (6200 मील) है; और इसका क्षेत्रफल 73556000 वर्ग किलोमीटर (28400000 वर्ग मील) है जिसमें लाल सागर और फारस की खाड़ी शामिल हैं।
सागर में जल की कुल मात्रा 292,131,000 घन किलोमीटर (70086000 घन मील) होने का अनुमान है। हिन्द महासागर में स्थित मुख्य द्वीप हैं; मेडागास्कर जो विश्व का चौथा सबसे बड़ा द्वीप है, रीयूनियन द्वीप; कोमोरोस; सेशेल्स, मालदीव, मॉरिशस, श्रीलंका और इंडोनेशिया का द्वीपसमूह जो इस महासागर की पूर्वी सीमा का निर्धारण करते हैं। इसकी आकृति विकृत 'एम'की भांति है।यह तीन और से भू-वेष्टित महासागर है। इसकी सीमाओं पर प्राचीन पठारी भूखण्ड स्थित हैं जो इस बात का संकेत देते हैं कि इस महासागर में गर्त एवं खाइयों का अभाव है। बीसवीं शताब्दी तक हिंद महासागर अज्ञात महासागर के नाम से जाना जाता था, लेकिन 1960 से 1965 के बीच अंतरराष्ट्रीय हिंद महासागरीय अभियान (IIOE) के फलस्वरूप इस महासागर की तली के सम्बन्ध में अनेक विलक्षण तथ्य प्रकाश में आए!\n\n\n"""
    assert got[9].data == "== इतिहास ==\n\n\n"


def test221_paragraphs_hi():
    """
    Split by paragraphs, hindi text, eos
    """
    opt = {"mode": "para", "eos": True}
    obj = mod.TextSrcDocument(DATADIR / "hi-indian-ocean.txt",
                              chunk_options=opt)
    got = list(obj)

    assert len(got) == 33
    assert got[0].data == """हिन्द महासागर दुनिया का तीसरा सबसे बड़ा समुद्र है और पृथ्वी की सतह पर उपस्थित पानी का लगभग 20% भाग इसमें समाहित है। उत्तर में यह भारतीय उपमहाद्वीप से, पश्चिम में पूर्व अफ्रीका; पूर्व में हिन्दचीन, सुंदा द्वीप समूह और ऑस्ट्रेलिया, तथा दक्षिण में दक्षिणध्रुवीय महासागर से घिरा है। विश्व में केवल यही एक महासागर है जिसका नाम किसी देश के नाम यानी, हिन्दुस्तान (भारत) के नाम है। प्राचीन भारतीय ग्रंथो में इसे "रत्नाकर" कहा गया है।\n"""
    assert got[20].data == "== इतिहास ==\n\n\n"
