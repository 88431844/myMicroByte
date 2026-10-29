from pathlib import Path
import sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Patch
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parents[1];doc=App.openDocument(str(ROOT/'output/v10/myMicrobyte_enclosure_v10.FCStd'))
f=FontProperties(fname='/System/Library/Fonts/Hiragino Sans GB.ttc')
plt.rcParams['font.family']=f.get_name();plt.rcParams['axes.unicode_minus']=False
fig,ax=plt.subplots(figsize=(9.5,7.2),dpi=180);fig.patch.set_facecolor('#eef2f5');ax.set_facecolor('#eef2f5')
colors=['#8095a8','#c9b183','#349a69','#45515a']
objs=[doc.FrontShell_v10,doc.RearShell_v10,doc.PowerSlider_v10,doc.Ref_Board]
for obj,c in zip(objs,colors):
 for w in obj.Shape.slice(App.Vector(0,1,0),-10.3186):
  p=w.discretize(Deflection=.015)
  ax.add_patch(Polygon([(v.x,v.z) for v in p],facecolor=c,edgecolor=c,linewidth=.7))
ax.set_xlim(37.5,45.5);ax.set_ylim(4,12.5);ax.set_aspect('equal');ax.axis('off')
def note(text,point,label,color='#253c4b'):
 ax.annotate(text,xy=point,xytext=label,fontproperties=f,fontsize=13,color=color,arrowprops=dict(arrowstyle='-',color=color),va='center')
def gap(a,b):ax.annotate('',xy=a,xytext=b,arrowprops=dict(arrowstyle='|-|',lw=1.1,color='#a6412d'))
gap((41.0,9.75),(41.,9.95));note('顶部间隙 0.20 mm',(41,9.85),(43.5,10.15),'#a6412d')
gap((40.05,6.1),(40.25,6.1));note('内侧间隙 0.20 mm',(40.15,6.1),(37.65,5.65),'#a6412d')
gap((41.85,8.35),(42.05,8.35));note('外侧间隙\n0.20 mm',(41.95,8.35),(43.5,8.5),'#a6412d')
gap((41.,5.35),(41.,5.55));note('底部间隙 0.20 mm',(41,5.45),(41.3,4.65),'#a6412d')
note('前盖一体限位面\n厚 1.70 mm',(41.4,10.75),(41,12.0))
note('后盖下导轨\n避开开关本体',(39.5,6.6),(37.65,7.55))
ax.text(40.75,7.9,'拨\n帽\n挡\n边',fontproperties=f,fontsize=13,va='center',color='white')
note('PCB',(39.2,9.4),(37.6,10.8))
fig.text(.05,.965,'v0.10 / 合盖后的拨帽导轨剖面',fontproperties=f,fontsize=22,color='#182c39',va='top')
fig.text(.05,.91,'截取宽挡边的一侧；几何来自实际 FreeCAD 模型。',fontproperties=f,fontsize=12,color='#465e70')
fig.legend(handles=[Patch(color=c,label=t) for c,t in zip(colors,['前盖','后盖','拨帽','PCB'])],loc='lower center',ncol=4,prop=f,frameon=False,bbox_to_anchor=(.5,.055))
fig.text(.05,.022,'这是设计间隙，未校准打印收缩；先清理毛边，再验证滑动手感及开关两档。',fontproperties=f,fontsize=12,color='#465e70')
fig.subplots_adjust(left=.025,right=.975,top=.87,bottom=.12)
fig.savefig(ROOT/'reports/v10/slider_guide_section.png',facecolor=fig.get_facecolor())
print('Saved actual CAD slider section')
