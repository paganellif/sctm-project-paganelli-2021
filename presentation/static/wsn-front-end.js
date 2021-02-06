var dataPointsHumidity = [];
var chartHumidity;
var dataPointsTemp = [];
var chartTemp;
var dataPointsSmoke = [];
var chartSmoke;
var dataPointsFlame = [];
var chartFlame;
var stations = [];
var index = 0;
var dataPointsHumidityMean = [];
var dataPointsTempMean = [];
var dataPointsSmokeMean = [];
var INIT_VALUES = 5;
var INIT_STATS = 5;
var server = "http://localhost:8080" //"http://18.189.151.46:8080"  // TODO: TO BE REPLACED "***********"

$(document).ready(function(){
    $(".sidenav").sidenav();

    $.getJSON(server+"/wsn", function(datarcv){
    var data = JSON.parse(datarcv);
        var html_code = "";
        for(var i = 0; i < data.agents_jid.length; i++){
            stations[i] = data["agents_jid"][i];
            html_code += '<li><a href="#" onclick="viewStation('+i+')">'+data["agents_jid"][i]+'</a></li>';
        }
        $("#mobile-demo").html(html_code);
        viewStation(0);
        renderInitAgentsValues(stations[index], 1);
        renderInitAgentsStats(stations[index], 1);
        showAgentInfo(stations[index]);
        window.setInterval(schedule, 10000);
    });
});

function schedule(){
    renderInitAgentsValues(stations[index], 1);
    renderInitAgentsStats(stations[index], 1);
    //if(!$('.modal').modal('isOpen')){
        showAgentInfo(stations[index]);
    //}
}

function viewStation(agent_jid_index){
    index = agent_jid_index;
    dataPointsHumidity = [];
    dataPointsTemp = [];
    dataPointsSmoke = [];
    dataPointsFlame = [];
    dataPointsHumidityMean = [];
    dataPointsTempMean = [];
    dataPointsSmokeMean = [];


    chartHumidity = new CanvasJS.Chart("chartContainerHum", {
        theme: "light2",
        title: {
            text: "Humidity"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: "Humidity"
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsHumidity
            }, {
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            name: "Average",
            type: "spline",
            dataPoints: dataPointsHumidityMean
            }]
    });

    chartTemp = new CanvasJS.Chart("chartContainerTemp", {
        theme: "light2",
        title: {
            text: "Temperature"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: "C°"
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsTemp
            }, {
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            name: "Average",
            type: "spline",
            dataPoints: dataPointsTempMean
            }]
    });

    chartSmoke = new CanvasJS.Chart("chartContainerSmoke", {
        theme: "light2",
        title: {
            text: "Smoke"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: "mg/mc"
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsSmoke
            }, {
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            name: "Average",
            type: "spline",
            dataPoints: dataPointsSmokeMean
            }]
    });

    chartFlame = new CanvasJS.Chart("chartContainerFlame", {
        theme: "light2",
        title: {
           text: "Flame"
        },
        axisX: {
            valueFormatString: "HH:mm:ss"
        },
        axisY: {
            tile: ""
        },
        data: [{
            xValueFormatString: "HH:mm:ss",
            xValueType: "dateTime",
            type: "spline",
            dataPoints: dataPointsFlame
        }]
    });

    render();
    showAgentInfo(stations[index])
    renderInitAgentsValues(stations[index], INIT_VALUES);
    renderInitAgentsStats(stations[index], INIT_STATS);
    $(".sidenav").sidenav('close');
}

function getAgentJIDs(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.status == 200){
            var data = JSON.parse(this.responseText);
            var html_code = "";
            for(var i = 0; i < data.agents_jid.length; i++){
                stations[i] = data["agents_jid"][i];
                html_code += '<li class="tab"><div> '+data["agents_jid"][i]+' </div></li>';
            }
            $("#agent_jid").html(html_code);
        }
    };
    xmlhttp.open("GET", server+"/wsn", true);
    xmlhttp.send();
}

function showAgentInfo(agent_jid){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
                $("#station").html(
                '<span class="card-title">'+stations[index]+'</span>'+
                '<p>State: '+data["config"]["state"]+'  Node: '+data["config"]["name"]+'  Type: '+data["config"]["type"]+'</p>'+
                '<p>Spread K: '+data["config"]["spreading_param"]+'  Logging: '+data["config"]["logging"]+'</p>'+
                '<p>Button Sampling: '+data["config"]["flame_samples"]+' times</p> | Debounce: '+data["config"]["flame_debounce"]+'</p>'+
                '<p>Trigger Event Num: '+data["config"]["trigger_events_num"]+'times | Trigger Event Time: '+data["config"]["trigger_events_period"]+'sec</p>'+
                '<p>Alarm Time: '+data["config"]["alarm_total_duration"]+'sec | Alarm Blink: '+data["config"]["alarm_period"]+'</p>'+
                '<p>CPU Freq: '+data["cpu"]["cpu_freq_cur"]+'Hz |Min: '+data["cpu"]["cpu_freq_min"]+'Hz |Max: '+data["cpu"]["cpu_freq_max"]+'Hz</p>'+
                '<p>CPU Avg Load: '+data["cpu"]["sys_avg_load_1"]+' last sec|'+data["cpu"]["sys_avg_load_5"]+' last 5 sec| '+data["cpu"]["sys_avg_load_15"]+' last 15 sec</p>'+
                '<p>CPU Temp: '+data["cpu"]["temp"]+'C°</p>'+
                '<p>Boot Time: '+data["cpu"]["boot_time"]+'</p>'+
                '<p><a class="waves-effect waves-light btn modal-trigger" href="#modal1">Modify Configs</a>'+
                '<div id="modal1" class="modal">'+
                   '<div class="modal-content">'+
                       '<div class="row">'+
                        '<form class="col s12" id="MyForm">'+
                         '<div class="row">'+
                            '<div class="input-field col s6">'+
                              '<input placeholder="'+data["config"]["spreading_param"]+'" id="spreadk" type="text" class="validate">'+
                              '<label for="spreadk">Spread K</label>'+
                            '</div>'+
                            '<div class="input-field col s6">'+
                              '<input placeholder="'+data["config"]["logging"]+'" id="logging" type="text" class="validate">'+
                              '<label for="logging">Logging</label>'+
                            '</div>'+
                          '</div>'+
                          '<div class="row">'+
                            '<div class="input-field col s6">'+
                              '<input placeholder="'+data["config"]["flame_samples"]+'" id="buttontimes" type="text" class="validate">'+
                              '<label for="buttontimes">Btn Sampling Times</label>'+
                            '</div>'+
                            '<div class="input-field col s6">'+
                              '<input placeholder="'+data["config"]["flame_debounce"]+'" id="buttondebounce" type="text" class="validate">'+
                              '<label for="buttondebounce">Btn Debounce</label>'+
                            '</div>'+
                          '</div>'+
                        '</form>'+
                      '</div>'+
                   '</div>'+
                   '<div class="modal-footer">'+
                     '<a href="#!" type="submit" name="action" class="modal-close waves-effect waves-green btn-flat">Confirm</a>'+
                   '</div>'+
                  '</div></p>'
              );

              $('.modal').modal();

              $('#MyForm').submit(function() {
                    // get all the inputs into an array.
                    var $inputs = $('#MyForm :input');
                    console.log($inputs)

                    // not sure if you wanted this, but I thought I'd add it.
                    // get an associative array of just the values.
                    var values = {};
                    $inputs.each(function() {
                        values[this.name] = $(this).val();
                    });

                    var xmlhttp = new XMLHttpRequest();
                    var params = "";

                    xmlhttp.setRequestHeader('Content-type', 'application/text');

                    xmlhttp.onreadystatechange = function() {
                        if(this.readyState == 4 && this.status == 200) {
                            alert("Configuration of node "+agent_jid+"modified!")
                        }
                    }

                    xmlhttp.open('POST', server+"/node/update/"+agent_jid, true);
                    xmlhttp.send(String(params));
              });
        }
    };
    xmlhttp.open("GET", server+"/node_info/"+agent_jid, true);
    xmlhttp.send();
}

function renderInitAgentsValues(jid, limit){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            console.log(data);
            for(var i = (data.length - 1); i >= 0 ; i--){
                dataPointsHumidity.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["hum"])});
                dataPointsTemp.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["temp"])});
                dataPointsSmoke.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["smoke"])});
                if(data[i]["flame"] == true){
                        dataPointsFlame.push({x: Date.parse(data[i]["timestamp"]), y: 1});
                } else {
                      dataPointsFlame.push({x: Date.parse(data[i]["timestamp"]), y: 0});
                }
            }
            render();
        }
    };
    xmlhttp.open("GET", server+"/value/"+jid+"?limit="+limit, true);
    xmlhttp.send();
}

function renderInitAgentsStats(jid, limit){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            console.log(data);
            for(var i = (data.length - 1); i >= 0 ; i--){
                dataPointsHumidityMean.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["hum_avg"])});
                dataPointsTempMean.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["temp_avg"])});
                dataPointsSmokeMean.push({x: Date.parse(data[i]["timestamp"]), y: parseFloat(data[i]["smoke_avg"])});
            }
            $("#hum_max").text("Max: "+data[0]["hum_max"].toFixed(2)+" %");
            $("#hum_min").text("Min: "+data[0]["hum_min"].toFixed(2)+" %");
            $("#temp_max").text("Max: "+data[0]["temp_max"].toFixed(2)+" C°");
            $("#temp_min").text("Min: "+data[0]["temp_min"].toFixed(2)+" C°");
            $("#smoke_max").text("Max: "+data[0]["smoke_max"].toFixed(5)+" mg/mc");
            $("#smoke_min").text("Min: "+data[0]["smoke_min"].toFixed(5)+" mg/mc");
            render();
        }
    };
    xmlhttp.open("GET", server+"/statistics/"+jid+"?limit="+limit, true);
    xmlhttp.send();
}

function render(){
      chartHumidity.render();
      chartTemp.render();
      chartSmoke.render();
      chartFlame.render();
}
