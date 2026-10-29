from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'reports/v10';O=ROOT/'output/v10'
F='/System/Library/Fonts/Hiragino Sans GB.ttc'
def font(n):return ImageFont.truetype(F,n)
BG='#17212a';CARD='#2a3948';FG='#ecf2f7';MUT='#b7c9d9';ACC='#9bdacb'
def base(h,title,subtitle):
 im=Image.new('RGB',(1700,h),BG);d=ImageDraw.Draw(im)
 d.text((42,26),title,font=font(36),fill=FG);d.text((42,80),subtitle,font=font(22),fill=MUT)
 return im,d
def panel(im,d,x,y,w,h,title,fn,crop=None):
 d.rounded_rectangle((x,y,x+w,y+h),radius=16,fill=CARD)
 d.text((x+24,y+18),title,font=font(27),fill=ACC)
 src=Image.open(R/fn).convert('RGB')
 if crop:src=src.crop(crop)
 src.thumbnail((w-16,h-72),Image.Resampling.LANCZOS)
 im.paste(src,(int(x+(w-src.width)/2),int(y+63+(h-72-src.height)/2)))
im,d=base(1390,'v0.10 / 借鉴 GBA 的一体拨帽与合盖防脱结构','宽挡边 + 中央叉口 + 后盖导轨 + 前盖整体限位；三件打印件，无独立压条。')
panel(im,d,28,130,810,530,'拨帽内侧 · 14 mm 宽挡边与叉口','slider_inner.png',(0,50,825,567))
panel(im,d,862,130,810,530,'拨帽外侧 · 防滑纹朝上打印','slider_outer.png',(0,50,825,567))
panel(im,d,28,684,810,530,'前盖落下 · 整体限位面随盖装入','front_roof_install.png',(0,45,825,567))
panel(im,d,862,684,810,530,'合盖后 · 宽挡边留在导轨内部','front_roof_closed.png',(0,45,825,567))
d.text((44,1241),'叉口宽 1.8 mm；叉根厚 1.6 mm；前盖限位面厚 1.7 mm。名义滑动间隙单边 0.2 mm。',font=font(24),fill=FG)
d.text((44,1288),'后盖平放 → 放入 PCB → 叉口套住开关拨杆 → 合前盖；合盖前仍需保持平放。',font=font(24),fill=MUT)
d.text((44,1335),'银／黄／绿仅用来区分结构，打印计划仍为全黑 PLA。本轮尚未打印。',font=font(24),fill=MUT)
im.save(O/'v10_gba_slider_review.png')
im,d=base(850,'v0.10 / 整机外观与爆炸图','使用实际 FreeCAD 网格；开关处壳壁局部加厚 0.55 mm，整机壳体最大宽度约 85.55 mm。')
panel(im,d,28,130,810,590,'合拢外观','whole_assembled.png',(0,45,825,567))
panel(im,d,862,130,810,590,'三件打印件与电子元件','whole_exploded.png',(0,45,825,567))
d.text((44,750),'保留 F3 凸框、小显示窗、整圈玻璃限位、平整后盖和喇叭自带胶定位座。',font=font(24),fill=FG)
d.text((44,798),'下一步实物验证：拨帽松紧、两档到位、螺丝拧紧后的屏幕状态。',font=font(23),fill=MUT)
im.save(O/'v10_assembly_review.png')
print('Saved v10 review plates')
