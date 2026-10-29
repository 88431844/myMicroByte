from pathlib import Path
import sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
doc=App.openDocument(str(ROOT/'output/v02/myMicrobyte_enclosure_v02.FCStd'))
im=Image.new('RGB',(1720,1120),'#f6f7f9');d=ImageDraw.Draw(im)
font='/System/Library/Fonts/STHeiti Medium.ttc'
def f(s):return ImageFont.truetype(font,s)
scale=15;cx,cy=720,560
def pt(x,y):return cx+x*scale,cy-y*scale
def rect(b):return [*pt(b[0],b[3]),*pt(b[2],b[1])]
def bb(o):
 b=o.Shape.BoundBox;return (b.XMin,b.YMin,b.XMax,b.YMax)
def dash_box(b,color):
 x0,y0,x1,y1=rect(b)
 for x in range(int(x0),int(x1),14):
  d.line((x,y0,min(x+7,x1),y0),fill=color,width=3);d.line((x,y1,min(x+7,x1),y1),fill=color,width=3)
 for y in range(int(y0),int(y1),14):
  d.line((x0,y,x0,min(y+7,y1)),fill=color,width=3);d.line((x1,y,x1,min(y+7,y1)),fill=color,width=3)
d.text((70,40),'myMicrobyte v0.2｜后壳内侧布局',font=f(38),fill='#222b35')
d.text((70,100),'实线：后壳内的电池与喇叭；虚线：上方 PCB 元件及端子投影（高度不同）',font=f(23),fill='#58636e')
d.rounded_rectangle(rect((-42.5,-22.5,42.5,22.5)),radius=82,fill='#d4d9df',outline='#465260',width=4)
d.rounded_rectangle(rect((-40.5,-20.5,40.5,20.5)),radius=52,fill='#e9edf1',outline='#7c8895',width=2)
for x in [-37.46,37.46]:
 for y in [-17.46,17.46]:
  a,b=pt(x,y);d.ellipse((a-45,b-45,a+45,b+45),fill='#b7c0c9',outline='#536170',width=2);d.ellipse((a-17,b-17,a+17,b+17),fill='#f6f7f9')
d.rectangle(rect(bb(doc.BatteryFrame)),outline='#bf8a27',width=5)
d.rectangle(rect(bb(doc.Battery_Assumed)),fill='#d2e6dc',outline='#3b8063',width=3)
d.rounded_rectangle(rect(bb(doc.SpeakerFrame)),radius=80,outline='#bf8a27',width=5)
d.rounded_rectangle(rect(bb(doc.Speaker_1510)),radius=75,fill='#b6c2cf',outline='#4c6079',width=3)
for name in ['Ref_U1','Ref_CARD1','USB_Envelope','BAT_ConnectorEnvelope','SPEAKER_ConnectorEnvelope']:
 dash_box(bb(doc.getObject(name)),'#557ca5')
for name in ['BAT_PlugEnvelope','SPEAKER_PlugEnvelope']:dash_box(bb(doc.getObject(name)),'#9e709b')
for text,x,y,size in [('ESP32',-26,0,25),('TF',3,13,25),('Type-C',-4,-17,19),('BAT',31.5,10,18),('SPK',-12,16,17)]:
 a,b=pt(x,y);d.text((a,b),text,font=f(size),fill='#284c72')
a,b=pt(-20,-8);d.text((a,b),'电池选型包络',font=f(28),fill='#245c45');d.text((a,b+40),'56 × 36 × 6 mm',font=f(28),fill='#245c45')
a,b=pt(33,4.5);d.text((a-30,b-30),'1510',font=f(22),fill='#26374b')
# Speaker leads head toward the SPEAKER plug via the TF side, above battery.
route=[pt(33,12),pt(30,14),pt(-4.939,15.433)]
d.line(route,fill='#ba5560',width=4)
for a,b in route:d.ellipse((a-4,b-4,a+4,b+4),fill='#ba5560')
d.text((1360,280),'定位框',font=f(27),fill='#986916')
d.text((1360,325),'内净空 57×37',font=f(23),fill='#384655')
d.text((1360,365),'壁厚 1.2 mm',font=f(23),fill='#384655')
d.text((1360,405),'框高 2.4 mm',font=f(23),fill='#384655')
d.text((1360,505),'喇叭朝后发声',font=f(27),fill='#384655')
d.text((1360,550),'15×10×3.5 mm',font=f(23),fill='#384655')
d.text((1360,595),'红线为喇叭走线',font=f(23),fill='#984751')
d.text((1360,635),'平面预估约 42 mm',font=f(21),fill='#984751')
d.text((70,970),'电池位于后壳内侧并用胶粘固定。尺寸指成品总包络，需包含保护板、包边及标签。',font=f(25),fill='#344350')
d.text((70,1015),'BAT / SPK 的 XY 来自 PCB 封装；端子与插头厚度使用保守占位，尚未按实物校准。',font=f(23),fill='#66717c')
d.text((70,1055),'本图从后壳内侧看向底板，坐标方向与正面装配一致；不是后壳外表面视图。',font=f(23),fill='#66717c')
im.save(ROOT/'reports/v02/layout_annotated.png')
print('Annotated layout saved')
