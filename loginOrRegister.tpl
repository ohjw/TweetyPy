<html>

<head>
<style type="text/css">
   body { font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif; color: #CCFFFF;}
   form { border:solid 1px #CCFFFF;width:300px; padding:100px;
		  background-color:#990033;
		  margin:auto; margin-top:100px;}
   ul { list-style-type:none; padding-left:0px }
   ul li { line-height:2.5em; }
   ul li span { float:left; width:80px; text-align:right; margin-right:8px; }
   input { text-align: center; width:150; background-color:#ffffff; border-radius: 10px; outline: none; }
   .heading { text-align:center; font-style: italic; font-size: 20pt; }
   input[type="submit"] {
        width: 100px;
        background: #CCFFFF;
        -webkit-border-radius: 30px;
        -moz-border-radius: 30px;
        border-radius: 30px;

        -webkit-box-shadow: 1px 1px 1px rgba(0,0,0, .29), inset 1px 1px 1px rgba(255,255,255, .44);
        -moz-box-shadow: 1px 1px 1px rgba(0,0,0, .29), inset 1px 1px 1px rgba(255,255,255, .44);
        box-shadow: 1px 1px 1px rgba(0,0,0, .29), inset 1px 1px 1px rgba(255,255,255, .44);

        -webkit-transition: all 0.15s ease;
        -moz-transition: all 0.15s ease;
        -o-transition: all 0.15s ease;
        -ms-transition: all 0.15s ease;
        transition: all 0.15s ease;
   }

   input[type="submit"]:hover{ background: #FFFF33;}
   #homeImage{ margin-top: -100px; margin-left: -50px; width:100px; }
   #link { margin-top:20px; text-align: center; margin-left: 22px; }
   #buttonHolder { margin-left: 25px; }
   #message { font-size: 15pt; text-align: center; }
   a { text-decoration: none; color: #FFFF33; font-size: 10pt; }
</style>
</head>

<body>

<form method="POST" action="{{post}}">
<div class = 'heading'> TweetyPy</div>
<div><img id = 'homeImage' src='http://wallpapercave.com/wp/dYlAC1J.png'></div>
<div id = 'message'>{{message}}</div>
<ul>
<li><span>Name</span> <input name="name" type="text"></li>
<li><span>Password</span><input name="password" type="password"></li>
<li id = "buttonHolder"><span>&nbsp;</span><input type="submit"></li>
</ul>
<div id="link">
    <a href="{{link}}">{{linkMessage}}</a>
</div>
</form>
			  
</body>
</html