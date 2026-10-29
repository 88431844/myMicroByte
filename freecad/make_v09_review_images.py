from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'reports/v09';O=ROOT/'output/v09'
F='/System/Library/Fonts/Hiragino Sans GB.ttc'
def font(n):return ImageFont.truetype(F,n)
BG='#17212a';CARD='#2a3948';FG='#ecf2f7';MUT='#b7c9d9';ACC='#9bdacb'
def base(h,title,subtitle):
 im=Image.new('RGB',(1700,h),BG);d=ImageDraw.Draw(im)
 d.text((42,26),title,font=font(36),fill=FG);d.text((42,80),subtitle,font=font(22),fill=MUT)
 return im,d
def panel(im,d,x,y,w,h,title,fn,crop=None):
 d.rounded_rectangle((x,y,x+w,y+h),radius=16,fill=CARD)
 d.text((x+24,y+18),title,font=font(28),fill=ACC)
 src=Image.open(R/fn).convert('RGB')
 if crop:src=src.crop(crop)
 src.thumbnail((w-16,h-72),Image.Resampling.LANCZOS)
 im.paste(src,(int(x+(w-src.width)/2),int(y+63+(h-72-src.height)/2)))
im,d=base(860,'v0.9 / 凸框前盖与整机爆炸图','以你选中的 F3 为基础；显示开口缩小，按键孔和前盖正面朝上的打印方向保留。')
panel(im,d,28,130,810,600,'合拢外观','front_assembled.png',(0,45,825,557))
panel(im,d,862,130,810,600,'装配分解','whole_exploded.png',(0,45,825,557))
d.text((44,758),'银色外壳、黄色压条、绿色拨帽仅用于看清结构；交互页默认全黑 PLA。',font=font(25),fill=FG)
d.text((44,803),'本轮四个打印件：前盖、后盖、拨帽、刚性压条。尚未发送打印。',font=font(23),fill=MUT)
im.save(O/'v09_assembly_review.png')
im,d=base(910,'v0.9 / 屏幕外围限位与避压间隙','限位框围住完整玻璃；显示窗口只露出显示区附近，遮边不贴压玻璃。')
panel(im,d,28,130,810,620,'前盖内侧 · 全周限位框','front_inside.png',(0,45,825,557))
panel(im,d,862,130,810,620,'玻璃右侧 · 实际 CAD 剖面','screen_clearance_section.png',(290,135,1300,1030))
d.text((44,778),'窗口 29.72 × 29.72 mm  /  显示区 27.72 × 27.72 mm  /  侧向留空 0.5 mm／边',font=font(25),fill=FG)
d.text((44,824),'按 1 mm 胶层计算，玻璃上方留空约 1.05 mm；胶厚不均及按压变形仍需实物验证。',font=font(24),fill=MUT)
im.save(O/'v09_screen_review.png')
im,d=base(1430,'v0.9 / 拨帽固定与后盖结构','取消两条细长拨帽弹片；喇叭使用自带胶，背部保持开放。')
panel(im,d,28,130,810,540,'厚压条从上方装入','keeper_install.png',(0,45,825,567))
panel(im,d,862,130,810,540,'落座后由前盖锁住','keeper_seated.png',(0,45,825,567))
panel(im,d,28,694,810,540,'椭圆喇叭座 + 开放矩形围壁','speaker_exploded.png',(0,45,825,557))
panel(im,d,862,694,810,540,'恢复平整背面和圆角','rear_exterior.png',(0,45,825,557))
d.text((44,1262),'压条横梁厚 1.5 mm；两端短插脚 1.2 × 2.8 mm。平放装配，合盖后才完全防脱。',font=font(24),fill=FG)
d.text((44,1309),'喇叭侧弹片、音腔盖和三个卡爪全部取消；椭圆座中间仍直通出声孔。',font=font(24),fill=MUT)
d.text((44,1356),'平整后盖没有离桌脚，桌面可能遮住声孔；开放围壁的音量效果需试听。',font=font(24),fill=MUT)
im.save(O/'v09_rear_slider_review.png')
print('Saved three CAD review plates')
