"""Preserve native FreeCAD view metadata when saving via the headless CAD API.

The view providers/material payloads are copied from already GUI-saved native
documents in this project. No geometry or document properties are changed.
"""
from pathlib import Path
import zipfile,copy,os,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'output/v06/myMicrobyte_enclosure_v06.FCStd'
with zipfile.ZipFile(ROOT/'output/myMicrobyte_enclosure_v01.FCStd') as old, zipfile.ZipFile(ROOT/'output/myMicrobyte_blackPLA_preview.FCStd') as preview, zipfile.ZipFile(path) as current:
    guio=ET.fromstring(old.read('GuiDocument.xml'));guip=ET.fromstring(preview.read('GuiDocument.xml'))
    oldviews={v.get('name'):v for v in guio.find('ViewProviderData')}
    previewviews={v.get('name'):v for v in guip.find('ViewProviderData')}
    doc=ET.fromstring(current.read('Document.xml'))
    objects=doc.find('Objects').findall('Object')
    native=ET.Element('Document',SchemaVersion='1',HasExpansion='1');ET.SubElement(native,'Expand')
    providers=ET.SubElement(native,'ViewProviderData',Count=str(len(objects)))
    payload={}
    for idx,obj in enumerate(objects):
        name=obj.get('name');typ=obj.get('type','')
        source=old
        template=oldviews.get(name)
        if name in ['RearShell_v06','FrontShell_v06','PowerSlider_v06','AcousticLid_v06'] or name.startswith('Button_'):
            source=preview;template=previewviews['Preview_RearShell']
        elif name in ['SpeakerFrontSeal','ChamberLidSeal']:
            template=oldviews['Ref_Board']
        elif name=='Speaker_1510':
            template=oldviews['USB_Envelope']
        if template is None:template=oldviews['PCBReference'] if 'Group' in typ else oldviews['RearShell']
        visible=name in ['RearShell_v06','FrontShell_v06','PowerSlider_v06','AcousticLid_v06','PCBReference','AcousticSeals','SpeakerFrontSeal','ChamberLidSeal','Hardware_v06','Battery_Assumed','LCD_Assumed_5mm','USB_Envelope','Speaker_1510'] or name.startswith('Button_') or name.startswith('Ref_') or name.startswith('Hardware_')
        v=copy.deepcopy(template);v.set('name',name);v.set('treeRank',str(idx));v.set('expanded','0')
        for prop in v.find('Properties'):
            if prop.get('name')=='Visibility':prop[0].set('value','true' if visible else 'false')
            for node in prop.iter():
                file=node.get('file')
                if file:
                    target=f'ViewData_{idx}_{file}'
                    payload[target]=source.read(file);node.set('file',target)
        providers.append(v)
    native.append(copy.deepcopy(guio.find('Camera')))
    tmp=path.with_suffix('.view.FCStd')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
        for item in current.infolist():
            if item.filename!='GuiDocument.xml':out.writestr(item,current.read(item.filename))
        out.writestr('GuiDocument.xml',ET.tostring(native,encoding='utf-8',xml_declaration=True))
        for name,data in payload.items():out.writestr(name,data)
os.replace(tmp,path)
print('Native view metadata saved:',len(objects),'objects')
