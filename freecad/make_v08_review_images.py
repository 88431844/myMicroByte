"""Compose actual CAD viewer exports; no invented product geometry."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'reports/v08';O=ROOT/'output/v08';O.mkdir(exist_ok=True)
font='/System/Library/Fonts/STHeiti Light.ttc'
def f(n):return ImageFont.truetype(font,n)
BG='#17212a';CARD='#2a3948';FG='#ecf2f7';MUT='#b7c9d9';ACC='#91d3c4'
def base(h,title,sub):
 im=Image.new('RGB',(1700,h),BG);d=ImageDraw.Draw(im)
 d.text((44,28),title,font=f(38),fill=FG);d.text((44,82),sub,font=f(23),fill=MUT)
 return im,d
def picture(im,file,box,crop=None):
 src=Image.open(R/file).convert('RGB')
 if crop:src=src.crop(crop)
 w,h=box[2]-box[0],box[3]-box[1];src.thumbnail((w,h),Image.Resampling.LANCZOS)
 im.paste(src,(box[0]+(w-src.width)//2,box[1]+(h-src.height)//2))
im,d=base(1100,'v0.8 / 两种前盖实模对比','仅改变外壳表面；屏幕不垫高。银色用于看清造型，交互页可切回黑色。')
for x,tag,title in [(30,'A','A  凸起屏幕框'),(865,'B','B  平面前盖')]:
 d.rounded_rectangle((x,128,x+805,1018),18,fill=CARD)
 d.text((x+26,151),title,font=f(31),fill=ACC)
 picture(im,f'front_{tag}_assembled.png',(x+10,205,x+795,650),(50,70,775,540))
 picture(im,f'front_{tag}_height.png',(x+8,669,x+797,854),(10,200,815,395))
 lines=['屏幕框比按键区高 1.2 mm','玻璃低于框顶约 1.9 mm'] if tag=='A' else ['屏幕框与按键区齐平','玻璃低于前盖约 0.7 mm']
 for i,line in enumerate(lines):d.text((x+26,881+i*42),line,font=f(27),fill=FG)
 d.text((x+26,972),'按键露出约 1.4 mm',font=f(24),fill=MUT)
d.text((44,1044),'两版均移除玻璃上方压边；按约 1 mm 胶层计算。尺寸为名义值，仍需实物试装。',font=f(24),fill=MUT)
im.save(O/'v08_front_comparison.png')
im,d=base(820,'v0.8 / A、B 爆炸装配图','共用后盖、PCB、拨帽与开窗音腔盖；每次装配只选一件前盖。')
for x,tag,title in [(30,'A','A  凸起屏幕框'),(865,'B','B  平面前盖')]:
 d.rounded_rectangle((x,128,x+805,735),18,fill=CARD);d.text((x+26,150),title,font=f(31),fill=ACC)
 picture(im,f'front_{tag}_exploded.png',(x+8,205,x+797,718),(0,50,825,550))
d.text((44,765),'真实 FreeCAD 网格预览 · 按键直接使用静音开关 · 本轮尚未打印',font=f(24),fill=MUT)
im.save(O/'v08_exploded_comparison.png')
im,d=base(1340,'v0.8 / 音腔与拨帽改动','零件颜色仅用于区分；结构均来自当前 FreeCAD 模型。')
for x,title,fn in [(30,'开窗固定框 / 背部保持通气','acoustic_exploded.png'),(865,'后盖底面 / 离桌 0.9 mm','desk_sound_path.png')]:
 d.rounded_rectangle((x,128,x+805,715),18,fill=CARD);d.text((x+26,151),title,font=f(28),fill=ACC)
 picture(im,fn,(x+8,213,x+797,700),(0,50,825,555))
d.rounded_rectangle((30,745,1670,1264),18,fill=CARD)
picture(im,'slider_closeup.png',(45,795,840,1240),(0,50,825,555))
d.text((885,790),'加长内侧横边 + 防脱弹片',font=f(30),fill=ACC)
for i,line in enumerate(['内侧横边：6.8 → 10.4 mm','叉槽宽度：1.95 → 1.65 mm','机械滑动范围：3.6 mm','装入时轻拨两侧弹片让位','前盖合上后继续限制上浮','外侧保留竖向防滑纹']):d.text((885,852+i*55),line,font=f(26),fill=FG)
d.text((44,1292),'音量、异响、开关到档及打印弹片松紧，均需下一轮实物验证。',font=f(24),fill=MUT)
im.save(O/'v08_acoustic_slider_details.png')
print('Saved 3 review plates under',O)
