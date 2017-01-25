var USERNAME, ROOMNAME;

var SocketMgr = {
    socket: null,
    init: function() {
	//var for socket connection
	SocketMgr.socket = io.connect("127.0.0.1:5000");
    },
    bindSocketEvents: function() {
	SocketMgr.socket.on("buf",function(data) {
	    Canvas.draw(data);
	});
	SocketMgr.socket.on("chat",function(data) {
	    var elem = document.createElement("p");
	    console.log(data.user);
	    elem.innerHTML = "<b>"+data.user+"</b> "+data.msg;
	    document.getElementById("chat-display").appendChild(elem);
	});
	SocketMgr.socket.on("clear",function(data) {
	    Canvas.ctx.clearRect(0,0,1000,800);
	});
	SocketMgr.socket.on("init",function(data) {
	    USERNAME = data.user;
	    ROOMNAME = data.room;
	    TurnCheck.updateTurn();
	    //SocketMgr.socket.emit("join",data);
	});
    },
};

var Canvas = {
    canv: null,
    panel: null,
    wrapper: null,
    ctx: null,
    color: "#000000",
    width: 3,
    init: function() {
	//initializing canvas settings
	this.canv = document.getElementById("canv");
	this.panel = document.getElementById("canvas-panel");
	this.wrapper = document.getElementById("canvas-wrapper");
	this.canv.width = 1000;
	this.canv.height = 800;
	this.ctx = this.canv.getContext("2d");
	this.ctx.lineWidth = 3;
	this.ctx.fillStyle = "#000";
	this.ctx.strokeStyle = "#000";
	this.ctx.lineCap = "round";
	//this.canv.imageSmoothingEnabled = false;
    },
    bindCanvasEvents: function() {
	var computeCanvasCoords = function(ix,iy) {
	    var cx = parseInt(getComputedStyle(Canvas.canv).width);
	    var cy = parseInt(getComputedStyle(Canvas.canv).height);
	    console.log("cy: "+cy);
	    var x = (ix - Canvas.wrapper.offsetLeft) / cx * 1000;
	    var y = ((iy - (window.innerHeight - cy)/2)) / cy * 800;
	    console.log("x: "+x+", "+"y: "+y);
	    return {x:x,y:y};
	};
      	var fx = function(e) {
	    console.log("e.clientX: "+e.clientX+", e.clientY: "+e.clientY);
	    var coords = computeCanvasCoords(e.clientX,e.clientY);
	    SocketMgr.socket.emit("draw",{x:coords.x,y:coords.y,isDrawing:true,color:Canvas.color,width:Canvas.width});
	    Canvas.ctx.lineTo(coords.x,coords.y);
      	    Canvas.ctx.stroke();
        };	
      	Canvas.canv.addEventListener("mousedown",function(e) {
	    var coords = computeCanvasCoords(e.clientX,e.clientY);
	    SocketMgr.socket.emit("draw",{x:coords.x,y:coords.y,isDrawing:false,color:Canvas.color,width:Canvas.width});
	    Canvas.ctx.strokeStyle = Canvas.color;
	    Canvas.ctx.lineWidth = Canvas.width;
	    Canvas.canv.style.cursor = "sw-resize";
      	    Canvas.ctx.beginPath();
	    Canvas.ctx.moveTo(coords.x,coords.y);
      	    Canvas.canv.addEventListener("mousemove",fx);
	    Canvas.canv.addEventListener("mouseoff",function() {
		Canvas.ctx.closePath();
	    });
	    Canvas.canv.addEventListener("mouseover",function(e) {
		var coords = computeCanvasCoords(e.clientX,e.clientY);
		Canvas.ctx.beginPath();
		Canvas.ctx.moveTo(coords.x,coords.y);
	    });
      	});
      	document.addEventListener("mouseup",function() {
      	    Canvas.canv.removeEventListener("mousemove",fx);
      	    Canvas.ctx.closePath();
	    Canvas.canv.style.cursor = "auto";
      	});
    },
    draw: function(data) {
	Canvas.ctx.strokeStyle = data.color;
	Canvas.ctx.lineWidth = data.width;
	if (!(data.isDrawing)) {
	    Canvas.ctx.closePath();
	    Canvas.ctx.beginPath();
	    Canvas.ctx.moveTo(data.x,data.y);
	}
	else {
	    Canvas.ctx.lineTo(data.x,data.y);
      	    Canvas.ctx.stroke();
	}
    },
};

//module so the turn flag can be accessed but not changed by the user
var TurnCheck = (function() {
    var isTurn = false;
    var module = {
	checkTurn: function() {
	    return isTurn;
	},
	updateTurn: function() {
	    isTurn = SocketMgr.socket.emit("turnreq");
	    return isTurn;
	}
    };
    return module;
})();

//init style for items that have variable css
var initStyle = function() {
    var width = window.innerWidth - (300 + 15 + 15); //width of viewport minus sidebar and margin
    Canvas.wrapper.style.width = Math.max(375,Math.min(width,1000))+"px";
    Canvas.wrapper.style.height = "100%";
    Canvas.wrapper.style.left = (window.innerWidth - (300 + parseInt(Canvas.wrapper.style.width,10)))/2+"px";
    Canvas.panel.style.width = "100%";
    Canvas.panel.style.height = Math.max(300,Math.min((width * 0.8),800))+"px";
};

//binding of events without a category
var bindMiscEvents = function() {
    var field = document.getElementById("chat-field");
    field.addEventListener("keypress", function(e) {
	if (e.which == 13 && !e.shiftKey && field.value != "") {
	    var data = {user:USERNAME,msg:field.value};
	    SocketMgr.socket.emit("message",data);
	    field.value = "";
	    var elem = document.createElement("p");
	    elem.style.color = "#4286f4";
	    elem.innerHTML = "<b><span style='color: #4286f4'>"+data.user+"</span></b> <span style='color: #000'>"+data.msg+"</span>";
	    document.getElementById("chat-display").appendChild(elem);
	}
    });
    window.addEventListener("resize", initStyle);
    var board = document.getElementById("erase-board");
    board.addEventListener("mouseover",function() {
	this.innerHTML = "[X] erase board";
    });
    board.addEventListener("mouseout",function() {
	console.log("hey");
	this.innerHTML = "[X]";
    });
    board.addEventListener("click",function() {
	SocketMgr.socket.emit("clear",{hey:"hey"});
	Canvas.ctx.clearRect(0,0,1000,800);
    });

    var hueCanv = document.getElementById("hue-canv");
    var pickColor = function(e) {
	hueBarInit();
	var offset = bar.offsetLeft+hueCanv.offsetLeft+2;//parseInt(bar.offsetLeft,10) + parseInt(hueCanv.offsetLeft,10);
	console.log(offset);
	console.log("e: "+e.clientX);
	var n = (Math.min(Math.max(e.clientX,offset),offset+200) - offset);
	console.log(n);
	var ctx = hueCanv.getContext("2d");
	var data = ctx.getImageData(n,0,1,1).data;
	console.log(data);
	ctx.fillStyle = "#333";
	ctx.fillRect(n-1,0,3,1);
	var r = data[0];
	var g = data[1];
	var b = data[2];
	var color = tinycolor("rgb("+r+","+g+","+b+")");
	console.log(color.toHexString());
	Canvas.color = color.toHexString();
    };
    hueCanv.addEventListener("mousedown", function() {
	bar.addEventListener("mousemove",pickColor);
    });
    document.addEventListener("mouseup", function(){
	bar.removeEventListener("mousemove",pickColor);
    });

    var sizeCanv = document.getElementById("size-canv");
    var pickSize = function(e) {
	sizeBarInit();
	var offset = bar.offsetLeft+sizeCanv.offsetLeft+3;
	var n = (Math.min(Math.max(e.clientX,offset),offset+150) - offset);
	var ctx = sizeCanv.getContext("2d");
	ctx.fillStyle = "#333";
	ctx.fillRect(n-1,0,3,40);
	var size = ((n/40)*7)+3;
	Canvas.width = size;
    };
    sizeCanv.addEventListener("mousedown", function() {
	bar.addEventListener("mousemove",pickSize);
    });
    document.addEventListener("mouseup", function(){
	bar.removeEventListener("mousemove",pickSize);
    });

    var bar = document.getElementById("bottom-tool-bar");
    bar.addEventListener("mouseover", function() {
	this.style.opacity = "1";
	this.style.bottom = "0";
    });
    bar.addEventListener("mouseout", function() {
	this.style.opacity = "0.75";
	this.style.bottom = "-60px";
    });
};

var pulseIndicator = function(str,ms) {
    var ind = document.getElementById("floating-indicator");
    var txt = document.getElementById("indicator-text");
    txt.innerHTML = str;
    ind.style.opacity = "1";
    setTimeout(function(){ind.style.opacity="0";}, ms);
};

var dispInfobar = function(str) {
    var bar = document.getElementById("top-info-bar");
    var txt = document.getElementById("indicator-text-2");
    if (str) {
	bar.style.top = "0";
	bar.style.opacity = "1";
	txt.innerHTML = str;
    }
    else {
	bar.style.opacity = "0";
	bar.style.top = "0";
    }  
};

var hueBarInit = function() {
    var canv = document.getElementById("hue-canv");
    var ctx = canv.getContext("2d");
    var w = canv.width-10;
    var h = canv.height;
    //canvas is actually 200x1 pixels, uses css to stretch it to 200x40
    for (var i=0; i<h; i++) {
	for (var j=0; j<=w; j++) {
	    var color = tinycolor("hsl("+(j/w)*360+",75%,50%)");
	    ctx.fillStyle = color.toHexString();
	    ctx.fillRect(j,i,1,1);
	}
	ctx.fillStyle = "#000";
	for (var j=1; j<=10; j++) {
	    ctx.fillRect(w+j,i,1,1);
	}
    }
};

var sizeBarInit = function() {
    var canv = document.getElementById("size-canv");
    var ctx = canv.getContext("2d");
    var w = canv.width;
    var h = canv.height;
    ctx.clearRect(0,0,w,h);
    ctx.moveTo(0,h);
    ctx.beginPath();
    ctx.lineTo(w,0);
    ctx.lineTo(w,h);
    ctx.lineTo(0,h);
    ctx.closePath();
    ctx.fillStyle = "#e7e7e7";
    ctx.fill();
};

var init = function() {
    SocketMgr.init();
    Canvas.init();
    SocketMgr.bindSocketEvents();
    initStyle();
    hueBarInit();
    sizeBarInit();
    Canvas.bindCanvasEvents();
    bindMiscEvents();
};
