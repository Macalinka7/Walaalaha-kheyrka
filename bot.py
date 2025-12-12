#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNELS_ENV = os.getenv("CHANNELS", "")
CHANNELS = [c.strip() for c in CHANNELS_ENV.split(",") if c.strip()]
OWNER_IDS_ENV = os.getenv("OWNER_IDS", "")
OWNER_IDS = [int(x) for x in OWNER_IDS_ENV.split(",") if x.strip().isdigit()]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Full welcome text (adkaar & ducooyin buuxa — sida aad codsatay, aan la soo gaabin)
WELCOME_TEXT = """🕋 ﷽ 🕋

لا إله إلا الله محمد رسول الله ﷺ

قال رسول الله ﷺ:
«بُنِيَ الْإِسْلَامُ عَلَى خَمْسٍ:
شَهَادَةِ أَنْ لاَ إِلَهَ إِلَّا الله
وَأَنَّ مُحَمَّداً رَسُولُ الله،
وَإِقَامِ الصَّلَاةِ،
وَإِيتَاءِ الزَّكَاةِ،
وَحَجِّ الْبَيْتِ،
وَصَوْمِ رَمَضَانَ».
[صحيح البخاري ومسلم]

﴿
وَأَمَّا مَنْ خَافَ مَقَامَ رَبِّهِ
وَنَهَى النَّفْسَ عَنِ الْهَوَى
فَإِنَّ الْجَنَّةَ هِيَ الْمَأْوَى
﴾

si,aad isticmaalka usii wado wax badana ubarato fadlan
Marka hore 🫆xaqiiji inaad Kusoobiirto kanaalada🪩 walaalaha kheyrka & Wadajirka 🤍

Buttons

[☾⋆☾⋆☾⋆☾⋆☾⋆☾⋆☾⋆]
https://t.me/halatWafail
[Walaalaha kheyrka Group]
https://t.me/WkhYrka_jecel
[Wllha kheyrka Channel]
https://t.me/W_khayrka
[🛸🎙🎙🎧🔊🎙🎙🛸]
https://t.me/barnaamij_chat
[ Website ]
https://t.me/puparty_bot/index?startapp=11037856

[✅️Xaqiiji inaad Kusoobiirtay🔄]

Marka bad xaqiiji lataabto hadii ay sax tahay inuu Kusoobiiray
Keen buttons kan cusub

[​📖 Jadwalka Casharada]

Kitaabada Maalmaha/Habeenada Saacadda
Tafsiirul Qur'aan Kariim Habeen. Sabti & Habeen. Isniin 🕑8:30pm
Miatu Xadiith Habeen. Axad & Habeen. Isniin 🕐6:40pm
Khulasaa Nuurul Yaqiin  Galab Isniin Talaado & Arbaco 🕑5:00pm

[🗓️ Jadwalka Subacyada]

Subac Subax Sabti ilaa Arbaco 🕐8:00am
Subac Duhur Sabti ilaa  Arbaco 🕑1:30pm
Subac S/Baqara Khamiis  🕑1:00pm
Subac S/Kahfi Jimco
🕐9:00am

[🅱️arnaamijyada🎙Suaalaha]

G. 🕑4:00 pm
Habeenka. Khamiista & jumcaha
🕐9:00pm

[🕋Adkaar🕌Ducooyin saxiix ah]
أدعية وأذكار
من السُّنّة الصَّحيحة
﷽
«اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ، وَأَبُوءُ بِذَنْبِي فَاغْفِرْ لِي فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ».
«اللَّهُمَّ إِنِّي ظَلَمْتُ نَفْسِي ظُلْمًا كَثِيرًا، وَلَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ، فَاغْفِرْ لِي مَغْفِرَةً مِنْ عِنْدِكَ وَارْحَمْنِي إِنَّك أَنْتَ الْغَفُورُ الرَّحِيمُ».
«رَبِّ اغْفِرْ لِي خَطِيئَتِي وَجَهْلِي وَإِسْرَافِي فِي أَمْرِي كُلِّهِ وَمَا أَنْتَ أَعْلَمُ بِهِ مِنِّي، اللَّهُمَّ اغْفِرْ لِي خَطَايَايَ وَعَمْدِي وَجَهْلِي وَهَزْلِي، وَكُلُّ ذَلِكَ عِنْدِي، اللَّهُمَّ اغْفِرْ لِي مَا قَدَّمْتُ وَمَا أَخَّرْتُ وَمَا أَسْرَرْتُ وَمَا أَعْلَنْتُ أَنْتَ الْمُقَدِّمُ وَأَنْتَ الْمُؤَخِّرُ وَأَنْتَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ».
«اللَّهُمَّ اغْفِرْ لِي ذَنْبِي كُلَّهُ، دِقَّهُ، وَجِلَّهُ، وَأَوَّلَهُ، وَآخِرَهُ، وَعَلَانِيَتَهُ، وَسِرَّهُ».
«اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ وَالْعَجْزِ وَالْكَسَلِ وَالْجُبْنِ وَالْبُخْلِ وَضَلَعِ الدَّيْنِ وَغَلَبَةِ الرِّجَالِ».
«اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْبُخْلِ، وَأَعُوذُ بِكَ مِنَ الْجُبْنِ، وَأَعُوذُ بِكَ أَنْ أُرَدَّ إِلَى أَرْذَلِ الْعُمُرِ، وَأَعُوذُ بِكَ مِنْ فِتْنَةِ الدُّنْيَا، وَأَعُوذُ بِكَ مِنْ عَذَابِ الْقَبْرِ».
«اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْكَسَلِ وَالْهَرَمِ وَالْمَأْثَمِ وَالْمَغْرَمِ، وَمِنْ فِتْنَةِ الْقَبْرِ وَعَذَابِ الْقَبْرِ، وَمِنْ فِتْنَةِ النَّارِ وَعَذَابِ النَّارِ، وَمِنْ شَرِّ فِتْنَةِ الْغِنَى، وَأَعُوذُ بِكَ مِنْ فِتْنَةِ الْفَقْرِ، وَأَعُوذُ بِكَ مِنْ فِتْنَةِ الْمَسِيحِ الدَّجَّالِ، اللَّهُمَّ اغْسِلْ عَنِّي خَطَايَايَ بِمَاءِ الثَّلْجِ وَالْبَرَدِ، وَنَقِّ قَلْبِي مِنَ الْخَطَايَا كَمَا نَقَّيْتَ الثَّوْبَ الْأَبْيَضَ مِنَ الدَّنَسِ، وَبَاعِدْ بَيْنِي وَبَيْنَ خَطَايَايَ كَمَا بَاعَدْتَ بَيْنَ الْمَشْرِقِ وَالْمَغْرِبِ».
«اللَّهُمَّ رَبَّ السَّمَوَاتِ وَرَبَّ الْأَرْضِ وَرَبَّ الْعَرْشِ الْعَظِيمِ، رَبَّنَا وَرَبَّ كُلِّ شَيْءٍ، فَالِقَ الْحَبِّ وَالنَّوَى وَمُنْزِلَ التَّوْرَاةِ وَالْإِنْجِيلِ وَالْفُرْقَانِ، أَعُوذُ بِكَ مِنْ شَرِّ كُلِّ شَيْءٍ أَنْتَ آخِذٌ بِنَاصِيَتِهِ، اللَّهُمَّ أَنْتَ الْأَوَّلُ فَلَيْسَ قَبْلَكَ شَيْءٌ، وَأَنْتَ الْآخِرُ فَلَيْسَ بَعْدَكَ شَيْءٌ، وَأَنْتَ الظَّاهِرُ فَلَيْسَ فَوْقَكَ شَيْءٌ، وَأَنْتَ الْبَاطِنُ فَلَيْسَ دُونَكَ شَيْءٌ، اقْضِ عَنَّا الدَّيْنَ وَأَغْنِنَا مِنَ الْفَقْرِ».
«اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ شَرِّ مَا عَمِلْتُ وَمِنْ شَرِّ مَا لَمْ أَعْمَلْ».
«اللَّهُمَّ أَصْلِحْ لِي دِينِي الَّذِي هُوَ عِصْمَةُ أَمْرِي، وَأَصْلِحْ لِي دُنْيَايَ الَّتِي فِيهَا مَعَاشِي، وَأَصْلِحْ لِي آخِرَتِي الَّتِي فِيهَا مَعَادِي وَاجْعَلِ الْحَيَاةَ زِيَادَةً لِي فِي كُلِّ خَيْرٍ، وَاجْعَلِ الْمَوْتَ رَاحَةً لِي مِنْ كُلِّ شَرٍّ».
«اللَّهُمَّ إِنِّي أَسْأَلُكَ الْهُدَى وَالتُّقَى وَالْعَفَافَ وَالْغِنَى».
«اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْعَجْزِ وَالْكَسَلِ، وَالْجُبْنِ وَالْبُخْلِ، وَالْهَرَمِ وَعَذَابِ الْقَبْرِ، اللَّهُمَّ آتِ نَفْسِي تَقْوَاهَا وَزَكِّهَا أَنْتَ خَيْرُ مَنْ زَكَّاهَا، أَنْتَ وَلِيُّهَا وَمَوْلَاهَا، اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ عِلْمٍ لَا يَنْفَعُ، وَمِنْ قَلْبٍ لَا يَخْشَعُ، وَمِنْ نَفْسٍ لَا تَشْبَعُ، وَمِنْ دَعْوَةٍ لَا يُسْتَجَابُ لَهَا».
«اللَّهُمَّ لَكَ أَسْلَمْتُ وَبِكَ آمَنْتُ، وَعَلَيْكَ تَوَكَّلْتُ وَإِلَيْكَ أَنَبْتُ وَبِكَ خَاصَمْتُ، اللَّهُمَّ إِنِّي أَعُوذُ بِعِزَّتِكَ لَا إِلَهَ إِلَّا أَنْتَ أَنْ تُضِلَّنِي، أَنْتَ الْحَيُّ الَّذِي لَا يَمُوتُ وَالْجِنُّ وَالْإِنْسُ يَمُوتُونَ
«اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ زَوَالِ نِعْمَتِكَ وَتَحَوُّلِ عَافِيَتِكَ وَفُجَاءَةِ نِقْمَتِكَ وَجَمِيعِ سَخَطِكَ».
«اللَّهُمَّ مُصَرِّفَ الْقُلُوبِ صَرِّفْ قُلُوبَنَا عَلَى طَاعَتِكَ».
«اللَّهُمَّ رَبَّ جَبْرَائِيلَ وَمِيكَائِيلَ وَإِسْرَافِيلَ، فَاطِرَ السَّمَوَاتِ وَالأَرْضِ، عَالِمَ الْغَيْبِ وَالشَّهَادَةِ، أَنْتَ تَحْكُمُ بَيْنَ عِبَادِكَ فِيمَا كَانُوا فِيهِ يَخْتَلِفُونَ، اهْدِنِي لِمَا اخْتُلِفَ فِيهِ مِنَ الْحَقِّ بِإِذْنِكَ، إِنَّكَ تَهْدِي مَنْ تَشَاءُ إِلَى صِرَاطٍ مُسْتَقِيمٍ».
«اللَّهُمَّ إِنِّي أَعُوذُ بِرِضَاكَ مِنْ سَخَطِكَ، وَبِمُعَافَاتِكَ مِنْ عُقُوبَتِكَ، وَأَعُوذُ بِكَ مِنْكَ، لَا أُحْصِي ثَنَاءً عَلَيْكَ، أَنْتَ كَمَا أَثْنَيْتَ عَلَى نَفْسِكَ».
«اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ جَهْدِ الْبَلَاءِ وَدَرَكِ الشَّقَاءِ وَسُوءِ الْقَضَاءِ وَشَمَاتَةِ الْأَعْدَاءِ».
«اللَّهُمَّ اجْعَلْ لِي فِي قَلْبِي نُورًا، وَفِي لِسَانِي نُورًا، وَفِي سَمْعِي نُورًا، وَفِي بَصَرِي نُورًا، وَمِنْ فَوْقِي نُورًا، وَمِنْ تَحْتِي نُورًا، وَعَنْ يَمِينِي نُورًا، وَعَنْ شِمَالِي نُورًا، وَمِنْ بَيْنِ يَدَيَّ نُورًا، وَمِنْ خَلْفِي نُورًا، وَاجْعَلْ فِي نَفْسِي نُورًا، وَأَعْظِمْ لِي نُورًا».
«اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنَ الْخَيْرِ كُلِّهِ عَاجِلِهِ وَآجِلِهِ مَا عَلِمْتُ مِنْهُ وَمَا لَمْ أَعْلَم،ْ وَأَعُوذُ بِكَ مِنَ الشَّرِّ كُلِّهِ عَاجِلِهِ وَآجِلِهِ مَا عَلِمْتُ مِنْهُ وَمَا لَمْ أَعْلَمْ، اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنْ خَيْرِ مَا سَأَلَكَ عَبْدُكَ وَنَبِيُّكَ، وَأَعُوذُ بِكَ مِنْ شَرِّ مَا عَاذَ بِهِ عَبْدُكَ وَنَبِيُّكَ، اللَّهُمَّ إِنِّي أَسْأَلُكَ الْجَنَّةَ وَمَا قَرَّبَ إِلَيْهَا مِنْ قَوْلٍ أَوْ عَمَلٍ، وَأَعُوذُ بِكَ مِنَ النَّارِ وَمَا قَرَّبَ إِلَيْهَا مِنْ قَوْلٍ أَوْ عَمَلٍ وَأَسْأَلُكَ أَنْ تَجْعَلَ كُلَّ قَضَاءٍ قَضَيْتَهُ لِي خَيْرًا».
«اللَّهُمَّ بِعِلْمِكَ الْغَيْبَ وَقُدْرَتِكَ عَلَى الْخَلْقِ أَحْيِنِي مَا عَلِمْتَ الْحَيَاةَ خَيْرًا لِي، وَتَوَفَّنِي إِذَا عَلِمْتَ الْوَفَاةَ خَيْرًا لِي، اللَّهُمَّ وَأَسْأَلُكَ خَشْيَتَكَ فِي الْغَيْبِ وَالشَّهَادَةِ، وَأَسْأَلُكَ كَلِمَةَ الْحَقِّ فِي الرِّضَا وَالْغَضَبِ، وَأَسْأَلُكَ الْقَصْدَ فِي الْفَقْرِ وَالْغِنَى، وَأَسْأَلُكَ نَعِيمًا لَا يَنْفَدُ، وَأَسْأَلُكَ قُرَّةَ عَيْنٍ لَا تَنْقَطِعُ، وَأَسْأَلُكَ الرِّضَاءَ بَعْدَ الْقَضَاءِ، وَأَسْأَلُكَ بَرْدَ الْعَيْشِ بَعْدَ الْمَوْتِ، وَأَسْأَلُكَ لَذَّةَ النَّظَرِ إِلَى وَجْهِكَ وَالشَّوْقَ إِلَى لِقَائِكَ فِي غَيْرِ ضَرَّاءَ مُضِرَّةٍ وَلَا فِتْنَةٍ مُضِلَّةٍ، اللَّهُمَّ زَيِّنَّا بِزِينَةِ الْإِيمَانِ، وَاجْعَلْنَا هُدَاةً مُهْتَدِينَ».
«اللَّهُمَّ إِنِّي أَسْأَلُكَ العَفْوَ وَالْعَافِيَةَ فِي الدُّنْيَا وَالْآخِرَةِ، اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ فِي דِينِي وَدُنْيَايَ وَأَهْلِي وَمَالِي، اللَّهُمَّ اسْتُרْ عَوْרَاتِي وَآمِنْ رَوْعَاتِي، وَاحْفَظْنِي مِنْ بَيْنِ يَدَيَّ وَمِنْ خَلْفِي وَعَنْ يَمِينِي وَعَنْ شِمَالِي وَمِنْ فَوْقِي، وَأَعُوذُ بِعَظَمَتِكَ أَنْ أُغْتَالَ مِنْ تَحْتِي».
«اللَّهُمَّ عَالِمَ الْغَيْبِ وَالشَّهَادَةِ، فَاطِرَ السَّمَوَاتِ وَالْأَرْضِ، رَبَّ كُلِّ شَيْءٍ وَمَلِيكَهُ، أَشْهَدُ أَنْ لَا إِلَهَ إِلَّا أَنْتَ، أَعُوذُ بِكَ مِنْ شَرِّ نَفْسِي وَشَرِّ الشَّيْطَانِ وَشِرْكِهِ».
«اللَّهُمَّ إِنِّي أَسْأَلُكَ الثَّبَاتَ فِي الأَمْرِ، وَالْعَزِيمَةَ عَلَى الرُّشْدِ، وَأَسْأَلُكَ مُوجِبَاتِ رَحْمَتِكَ، وَعَزَائِمَ مَغْفِرَتِكَ، وَأَسْأَلُكَ شُكْرَ نِعْمَتِكَ، وَحُسْنَ عِبَادَتِكَ، وَأَسْأَلُكَ قَلْبًا سَلِيمًا، וَلِسَانًا صَادِقًا، وَأَسْأَلُكَ مِنْ خَيْرِ مَا تَعْلَمُ، وَأَعُوذُ بِكَ مِنْ شَرِّ مَا تَعْلَمُ، وَأَسْتَغْفِرُكَ لِمَا تَعْلَمُ، إِنَّكَ أَنْتَ عَلَّامُ الْغُيُوبِ».
«اللَّهُمَّ اكْفِنِي بِحَلَالِكَ عَنْ حَرَامِكَ وَأَغْنِنِي بِفَضْلِكَ عَمَّنْ سِوَاكَ».
«اللَّهُمَّ عَافِنِي فِي بَدَنِي، اللَّهُمَّ عَافِنِي فِي سَمْعِي، اللَّهُمَّ عَافِنِي فِي بَصَرِي، لَا إِلَهَ إِلَّا أَنْتَ، اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْكُفْرِ وَالْفَقْرِ، اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ عَذَابِ الْقَبْرِ، لَا إِلَهَ إِلَّا أَنْتَ».
«رَبِّ أَعِنِّي وَلَا تُعِنْ عَلَيَّ، وَانْصُرْنِي وَلَا تَنْصُرْ عَلَيَّ، وَامْكُرْ لِي وَلَا تَمْكُرْ عَلَيَّ، وَاهْدِنِي وَيَسِّرِ الْهُدَى لِي، وَانْصُرْنِي عَلَى مَنْ بَغَى عَلَيَّ، رَبِّ اجْعَلْنِي لَكَ شَكَّارًا، لَكَ ذَكَّارًا، لَكَ رَهَّابًا، لَكَ مِطْوَاعًا، لَكَ مُخْبِتًا إِلَيْكَ أَوَّاهًا مُنِيبًا، رَبِّ تَقَبَّلْ تَوْبَتِي وَاغْسِلْ حَوْبَتِي وَأَجِبْ دَعْوَتِي وَثَبِّتْ حُجَّتِي وَسَدِّدْ لِسَانِي وَاهْدِ قَلْبِي وَاسْلُلْ سَخِيمَةَ صَدْرِي».
«اللَّهُمَّ لَكَ الْحَمْدُ كُلُّهُ، اللَّهُمَّ لَا قَابِضَ لِمَا بَسَطْتَ، وَلَا بَاسِطَ لِمَا قَبَضْتَ، وَلَا هَادِيَ لِمَا أَضْلَلْت، وَلَا مُضِلَّ لِمَنْ هَدَيْتَ، وَلَا مُعْطِيَ لِمَا مَنَعْتَ، وَلَا مَانِعَ لِمَا أَعْطَيْتَ، وَلَا مُقَرِّبَ لِمَا بَاعَدْتَ، وَلَا مُبَاعِدَ لِمَا قَرَّبْتَ، اللَّهُمَّ ابْسُطْ عَلَيْنَا مِنْ بَرَكَاتِكَ وَرَحْمَتِكَ وَفَضْلِكَ وَرِزْقِكَ، اللَّهُمَّ إِنِّي أَسْأَلُكَ النَّعِيمَ الْمُقِيمَ الَّذِي لَا يَحُولُ وَلَا يَزُولُ، اللَّهُمَّ إِنِّي أَسْأَلُكَ النَّعِيمَ يَوْمَ الْعَيْلَةِ، وَالْأَمْنَ يَوْمَ الْخَوْفِ، اللَّهُمَّ إِنِّي عَائِذٌ بِكَ مِنْ شَرِّ مَا أَعْطَيْتَنَا وَشَرِّ مَا مَنَعْتَ، اللَّهُمَّ حَبِّبْ إِلَيْنَا الْإِيمَانَ وَزَيِّنْهُ فِي قُلُوبِنَا، وَكَرِّهْ إِلَيْنَا الْكُفْرَ وَالْفُسُوقَ وَالْعِصْيَانَ، وَاجْعَلْنَا مِنَ الرَّاشِدِينَ، اللَّهُمَّ تَوَفَّنَا مُسْلِمِينَ، وَأَحْيِنَا مُسْلِمِينَ، وَأَلْحِقْنَا بِالصَّالِحِينَ غَيْرَ خَزَايَا وَلَا مَفْتُونِينَ، اللَّهُمَّ قَاتِلْ الْكَفَرَةَ الَّذِينَ يُكَذِّبُونَ رُسُلَكَ، وَيَصُدُّونَ عَنْ سَبِيلِكَ، وَاجْعَلْ عَلَيْهِمْ رِجْزَكَ وَعَذَابَكَ، اللَّهُمَّ قَاتِلْ الْكَفَرَةَ الَّذِينَ أُوتُوا الْكِتَابَ إِلَهَ الْحَقِّ».
«اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّדٍ كَمَا صَلَّيْتَ عَلَى إِبْرَاهِيمَ وعَلَى آلِ إِبْرَاهِيمَ، إِنَّكَ حَمِيدٌ مَجِيدٌ، اللّٰهُمَّ بَارِكْ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا بَارَكْتَ عَلَى إِبْרَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ»*.

[🕌Towbadkeen🕌]

باب التوبة

﴿وَلَيْسَتِ التَّوْبَةُ لِلَّذِينَ يَعْمَلُونَ السَّيِّئَاتِ حَتَّىٰ إِذَا حَضَرَ أَحَدَهُمُ الْمَوْتُ قَالَ إِنِّي تُبْتُ الْآنَ وَلَا الَّذِينَ يَمُوتُونَ وَهُمْ كُفَّارٌ ۚ أُولَٰئِكَ أَعْتَدْنَا لَهُمْ عَذَابًا أَلِيمًا﴾
[ النساء: 18]

﴿ ۞ قُلْ يَا عِبَادِيَ الَّذِينَ أَسْرَفُوا عَلَىٰ أَنفُسِهِمْ لَا تَقْنَطُوا مِن رَّحْمَةِ اللَّهِ ۚ إِنَّ اللَّهَ يَغْفِرُ الذُّنُوبَ جَمِيعًا ۚ إِنَّهُ هُوَ الْغَفُورُ الرَّحِيمُ﴾
[ الزمر: 53]

قَالَ العلماءُ: التَّوْبَةُ وَاجبَةٌ مِنْ كُلِّ ذَنْب، فإنْ كَانتِ المَعْصِيَةُ بَيْنَ العَبْدِ وبَيْنَ اللهِ تَعَالَى لاَ تَتَعلَّقُ بحقّ آدَمِيٍّ، فَلَهَا ثَلاثَةُ شُرُوط:

أحَدُها: أنْ يُقلِعَ عَنِ المَعصِيَةِ.

والثَّانِي: أَنْ يَنْدَمَ عَلَى فِعْلِهَا.

والثَّالثُ: أَنْ يَعْزِمَ أَنْ لا يعُودَ إِلَيْهَا أَبَدًا. فَإِنْ فُقِدَ أَحَدُ الثَّلاثَةِ لَمْ تَصِحَّ تَوْبَتُهُ.

وإنْ كَانَتِ المَعْصِيَةُ تَتَعَلقُ بآدَمِيٍّ فَشُرُوطُهَا أرْبَعَةٌ: هذِهِ الثَّلاثَةُ، وأنْ يَبْرَأ مِنْ حَقّ صَاحِبِها، فَإِنْ كَانَتْ مالًا أَوْ نَحْوَهُ رَدَّهُ إِلَيْه، وإنْ كَانَت حَدَّ قَذْفٍ ونَحْوَهُ مَكَّنَهُ مِنْهُ أَوْ طَلَبَ عَفْوَهُ، وإنْ كَانَت غِيبَةً استَحَلَّهُ مِنْهَا، ويجِبُ أنْ يَتُوبَ مِنْ جميعِ الذُّنُوبِ، فَإِنْ تَابَ مِنْ بَعْضِها صَحَّتْ تَوْبَتُهُ عِنْدَ أهْلِ الحَقِّ مِنْ ذلِكَ الذَّنْبِ، وبَقِيَ عَلَيهِ البَاقي. وَقَدْ تَظَاهَرَتْ دَلائِلُ الكتَابِ، والسُّنَّةِ، وإجْمَاعِ الأُمَّةِ عَلَى وُجوبِ التَّوبةِ:

قَالَ الله تَعَالَى: وَتُوبُوا إِلَى اللَّهِ جَمِيعًا أَيُّهَا الْمُؤْمِنُونَ لَعَلَّكُمْ تُفْلِحُونَ [النور:31]، وَقالَ تَعَالَى: اسْتَغْفِرُوا رَبَّكُمْ ثُمَّ تُوبُوا إِلَيْهِ [هود:3]، وَقالَ تَعَالَى: يَا أَيُّهَا الَّذِينَ آمَنُوا تُوبُوا إِلَى اللَّهِ تَوْبَةً نَصُوحًا [التحريم:8].

1/13- وعَنْ أبي هُرَيْرَةَ  قالَ: سمِعتُ رَسُولَ اللهِ ﷺ يَقُولُ: واللَّه إِنِّي لأَسْتَغْفرُ الله، وَأَتُوبُ إِليْه، في اليَوْمِ، أَكثر مِنْ سَبْعِين مرَّةً رواه البخاري.

2/14- وعن الأَغَرِّ بْن يَسار المُزنِيِّ  قال: قال رسول الله ﷺ: يَا أَيُّها النَّاس تُوبُوا إِلى اللَّهِ واسْتغْفرُوهُ فإِني أَتوبُ في اليَوْمِ مائة مَرَّة رواه مسلم.

3/15- وعنْ أبي حَمْزَةَ أَنَس بنِ مَالِكٍ الأَنْصَارِيِّ خَادِمِ رسولِ الله ﷺ،  قال: قال رسول الله ﷺ: للَّهُ أَفْرحُ بتْوبةِ عَبْدِهِ مِنْ أَحَدِكُمْ سقطَ عَلَى بعِيرِهِ وقد أَضلَّهُ في أَرضٍ فَلاةٍ متفقٌ عليه.

وفي رواية لمُسْلمٍ: للَّهُ أَشدُّ فَرَحًا بِتَوْبَةِ عَبْدِهِ حِين يتُوبُ إِلَيْهِ مِنْ أَحَدِكُمْ كَانَ عَلَى راحِلَتِهِ بِأَرْضٍ فلاةٍ، فانْفلتتْ مِنْهُ وعلَيْها طعامُهُ وشرَابُهُ فأَيِسَ مِنْهَا، فأَتَى شَجَرةً فاضْطَجَعَ في ظِلِّهَا، وقد أَيِسَ مِنْ رَاحِلَتِهِ، فَبَيْنما هوَ كَذَلِكَ إِذْ هُوَ بِها قَائِمة عِنْدَهُ، فَأَخذ بِخطامِهَا ثُمَّ قَالَ مِنْ شِدَّةِ الفَرحِ: اللَّهُمَّ أَنت عبْدِي وأَنا ربُّكَ، أَخْطَأَ مِنْ شِدَّةِ الفَرح
"""

# Build keyboard for /start: channel links + Verify
def start_keyboard():
    buttons = []
    for ch in CHANNELS:
        if ch.startswith('@'):
            buttons.append([InlineKeyboardButton(ch, url=f"https://t.me/{ch.lstrip('@')}")])
    # Verify button
    buttons.append([InlineKeyboardButton("✅ Xaqiiji", callback_data="verify_subs")])
    return InlineKeyboardMarkup(buttons)

# Helper: split and send long messages (Telegram limit ~4096; use safe chunk)
def chunk_text(text, limit=3900):
    parts = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            parts.append(remaining)
            break
        # try to split at newline for nicer chunks
        idx = remaining.rfind('\n', 0, limit)
        if idx == -1:
            idx = limit
        parts.append(remaining[:idx].strip())
        remaining = remaining[idx:].strip()
    return parts

async def send_long_message(bot, chat_id, text, reply_markup=None):
    parts = chunk_text(text)
    for i, p in enumerate(parts):
        markup = reply_markup if i == len(parts) - 1 else None
        await bot.send_message(chat_id=chat_id, text=p, reply_markup=markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send the full welcome (may be split if long)
    await send_long_message(context.bot, update.effective_chat.id, WELCOME_TEXT, reply_markup=start_keyboard())

# Verify subscriptions handler
async def verify_subs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    missing = []
    for ch in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ("left", "kicked"):
                missing.append(ch)
        except Exception as e:
            logger.warning("Could not check membership for %s: %s", ch, e)
            missing.append(ch)
    if not missing:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Jadwalka Casharada", callback_data="jadwal_cash")],
            [InlineKeyboardButton("🗓 Jadwalka Subacyada", callback_data="jadwal_sub")],
            [InlineKeyboardButton("🕌 Adkaar", callback_data="adkaar")],
        ])
        await query.edit_message_text("Waad ku mahadsan tahay! Waxaa lagu xaqiijiyey inaad kusoo biirtay kanaalada ✅", reply_markup=keyboard)
    else:
        buttons = []
        for ch in missing:
            if ch.startswith('@'):
                buttons.append([InlineKeyboardButton(ch, url=f"https://t.me/{ch.lstrip('@')}")])
        buttons.append([InlineKeyboardButton("Markale hubi", callback_data="verify_subs")])
        await query.edit_message_text(
            "Weli ma kusoo biirin kanaalada soo socda. Fadlan ku biir adigoo taabanaya links-ka kadibna riix Markale hubi.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Simple menu callbacks
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "jadwal_cash":
        await query.edit_message_text("📖 Jadwalka Casharada:\nTafsiirul Qur'aan Kariim Habeen: Sabti & Isniin 8:30pm\nMiatu Xadiith: Axad 6:40pm\nKhulasaa Nuurul Yaqiin: Isniin/Talaado/Arbaco 5:00pm")
    elif data == "jadwal_sub":
        await query.edit_message_text("🗓 Jadwalka Subacyada:\nSabti-Arbaco Subax 8:00am, Duhur 1:30pm; Khamiis Baqara 1:00pm; Jimco Kahfi 9:00am")
    elif data == "adkaar":
        await query.edit_message_text("🕋 Adkaar & Ducooyin (kooban):\n- اللَّهُمَّ اغْفِرْ لِي\n- رَبِّ اغْفِرْ لِي وَارْحَمْنِي")

# -------------------------
# Admin commands & scheduler
# -------------------------
SCHEDULE_FILE = "scheduled_jobs.json"

def load_jobs():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

scheduler = AsyncIOScheduler()

def is_user_owner(user_id: int):
    if not OWNER_IDS:
        return False
    return user_id in OWNER_IDS

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_owner(user_id):
        await update.message.reply_text("Adiga ma tihid owner-ka la oggol yahay.")
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Isticmaal: /broadcast Your message here")
        return
    targets = CHANNELS
    success = 0
    for t in targets:
        try:
            await context.bot.send_message(chat_id=t, text=text)
            success += 1
        except Exception as e:
            logger.warning("Failed to send to %s: %s", t, e)
    await update.message.reply_text(f"Broadcasted to {success}/{len(targets)} targets.")

async def setrecurring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_owner(user_id):
        await update.message.reply_text("Adiga ma tihid owner-ka la oggol yahay.")
        return
    if len(context.args) < 3:
        await update.message.reply_text("Isticmaal: /setrecurring <chat_id> <minute> <text...>\nTusaale: /setrecurring @mygroup 30 Fiid wanaagsan")
        return
    chat_id = context.args[0]
    minute = context.args[1]
    text = " ".join(context.args[2:])
    job_id = f"job_{int(datetime.now().timestamp())}"
    job = {
        "id": job_id,
        "type": "cron",
        "trigger_args": {"minute": minute},
        "chat_id": chat_id,
        "text": text
    }
    jobs = load_jobs()
    jobs.append(job)
    save_jobs(jobs)
    try:
        scheduler.add_job(
            lambda app=context.application, data=job: app.create_task(app.bot.send_message(chat_id=data["chat_id"], text=data["text"])),
            trigger="cron",
            id=job_id,
            **job["trigger_args"]
        )
        await update.message.reply_text(f"Job scheduled with id {job_id}")
    except Exception as e:
        logger.exception("Error scheduling job: %s", e)
        await update.message.reply_text("Waxaa dhacay khalad waqtiga la dhigayo.")

async def listrecurring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_owner(user_id):
        await update.message.reply_text("Adiga ma tihid owner-ka la oggol yahay.")
        return
    jobs = load_jobs()
    if not jobs:
        await update.message.reply_text("Ma jiraan jobs la keydiyey.")
        return
    lines = []
    for j in jobs:
        lines.append(f"- {j['id']}: chat={j['chat_id']} text={j['text']} trigger={j.get('trigger_args')}")
    await update.message.reply_text("\n".join(lines))

def restore_jobs(app):
    jobs = load_jobs()
    for j in jobs:
        try:
            scheduler.add_job(
                lambda app=app, data=j: app.create_task(app.bot.send_message(chat_id=data["chat_id"], text=data["text"])),
                trigger="cron" if j.get("type")=="cron" else "interval",
                id=j["id"],
                **(j.get("trigger_args", {}))
            )
            logger.info("Restored job %s", j["id"])
        except Exception as e:
            logger.exception("Error restoring job %s: %s", j.get("id"), e)

def main():
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN ma jiro. Fadlan buuxi .env.")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_subs_callback, pattern="^verify_subs$"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^(jadwal_cash|jadwal_sub|adkaar)$"))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("setrecurring", setrecurring))
    app.add_handler(CommandHandler("listrecurring", listrecurring))

    scheduler.start()
    restore_jobs(app)
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
