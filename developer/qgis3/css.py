#    border: 1px solid black;
css_sheet = (
    """
        QDockWidget::title {
            background: rgb(200, 200, 200); 
            text-align: left;
        }
        
        QDockWidget::title:hover {
            background: darkgray;
        }
            
        QDockWidget::float-button {
            image: url(C:/Users/DHKIM/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/dock_widet_template/icon.png);
        }
        
        QStackedWidget#stackedWidget{
            border: 1px solid;
            border-color: rgb(200, 200, 200);
        }

    
        QgsMapCanvas#widget{border-style: outset;border-width: 0.5px;border-color:gray;}
    """
)