from pathlib import Path
import sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parents[1];doc=App.openDocument(str(ROOT/'output/v09/myMicrobyte_enclosure_v09.FCStd'))
f=FontProperties(fname='/System/Library/Fonts/Hiragino Sans GB.ttc')
plt.rcParams['font.family']=f.get_name();plt.rcParams['axes.unicode_minus']=False
fig,ax=plt.subplots(figsize=(9.0,6.2),dpi=180);fig.patch.set_facecolor('#eef2f5');ax.set_facecolor('#eef2f5')
for obj,c in [(doc.FrontShell_v09,'#7d8b98'),(doc.Ref_Board,'#39976e'),(doc.LCD_AdhesiveEnvelope,'#d6a441'),(doc.LCD_Assumed_5mm,'#30638a')]:
 for w in obj.Shape.slice(App.Vector(0,1,0),.123):
  p=w.discretize(Deflection=.02)
  ax.add_patch(Polygon([(v.x,v.z) for v in p],facecolor=c,edgecolor=c,linewidth=1))
ax.set_xlim(13.5,20.0);ax.set_ylim(10.0,16.4);ax.set_aspect('equal');ax.axis('off')
ax.annotate('',xy=(15.4,14.55),xytext=(15.4,13.50005),arrowprops=dict(arrowstyle='<->',lw=1.8,color='#b04e2d'))
ax.text(13.7,14.0,'约1.05 mm\n玻璃上方留空',fontproperties=f,fontsize=13,color='#914028',va='center')
ax.annotate('',xy=(16.37,12.3),xytext=(15.87,12.3),arrowprops=dict(arrowstyle='<->',lw=1.5,color='#b04e2d'))
ax.annotate('侧隙0.5 mm',xy=(16.13,12.3),xytext=(17.7,11.7),fontproperties=f,fontsize=13,color='#914028',arrowprops=dict(arrowstyle='-',color='#914028'))
ax.annotate('前盖限位框',xy=(17.05,12.6),xytext=(18.0,13.5),fontproperties=f,fontsize=13,color='#324858',arrowprops=dict(arrowstyle='-',color='#324858'))
ax.text(14.0,12.65,'玻璃',fontproperties=f,fontsize=14,color='white')
ax.text(14.0,11.1,'原胶层',fontproperties=f,fontsize=12,color='#332911')
ax.text(17.9,10.38,'PCB',fontproperties=f,fontsize=12,color='white')
ax.annotate('显示窗口边缘',xy=(15.0,15.25),xytext=(13.7,15.9),fontproperties=f,fontsize=12,color='#324858',arrowprops=dict(arrowstyle='-',color='#324858'))
ax.text(18.0,14.3,'按键区\n外表面',fontproperties=f,fontsize=11,color='#324858')
fig.text(.06,.96,'屏幕右侧局部剖面 · 来自 v0.9 CAD',fontproperties=f,fontsize=20,color='#182c39',va='top')
fig.text(.06,.035,'按约1 mm原胶层计算。限位框防侧移，遮边与玻璃留空，不承担压紧固定。',fontproperties=f,fontsize=12,color='#465e70')
fig.subplots_adjust(left=.04,right=.97,top=.89,bottom=.10)
fig.savefig(ROOT/'reports/v09/screen_clearance_section.png',facecolor=fig.get_facecolor())
print('Saved CAD section diagram')
