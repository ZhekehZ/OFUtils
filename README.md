# OFUtils

OpenFlow utilities and applications for the OpenDayLight controller

### HOW-TO-RUN
 - Launch OpenDayLight and prepare the network 
    If you have mininet and OFManager, you can just configure ``launch.sh`` and run it
    ```sh
        # Configure the following lines:
        #   OpenDaylight="~/Загрузки/karaf-0.8.4/"
        #   OpenFlowApp="~/Загрузки/OpenDaylight-Openflow-App/"
        $ ./launch.sh
    ```
   Do not forget to call the ``pingall`` in minnet
 - Run the application, for example
    ```bash
        $ python3 Apps/TopologyVisualizer.py
    ```
    [![Пример](https://github.com/ZhekehZ/OFUtils/blob/master/ex.png)]
