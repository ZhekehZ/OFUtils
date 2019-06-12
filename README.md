# OFUtils

An application for configuring OpenFlow tables Application for configuring OpenFlow tables from an SDN network managed by an OpenDaylight controller.

### Prerequirement:
 - OpenDyalight controller with plugins:
   - odl-restconf-all
   - odl-openflowplugin-all
   - odl-mdsal-all
 - Python 3 and following libs:
   - tkinter
   - networkx
   - numpy
   - matplotlib
   - requests
   - threading
   - json2xml
   
### Launch
  1. Start OpenDaylight controller
  2. Run``` ./main.py```
  
  
 If you have mininet and OFManager, you can just configure ``launch.sh`` and run it
 ```sh
     # Configure the following lines:
     #   OpenDaylight="~/Загрузки/karaf-0.8.4/"
     #   OpenFlowApp="~/Загрузки/OpenDaylight-Openflow-App/"
     $ ./launch.sh
 ```
 ![Network topology](https://github.com/ZhekehZ/OFUtils/blob/master/ex.jpg)
 ![Flow editor](https://github.com/ZhekehZ/OFUtils/blob/master/ex2.jpg)
