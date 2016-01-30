<html>
  <head>
    <title>TweetyPy</title>
    <link rel="icon"
      type="image/png"
      href="http://wallpapercave.com/wp/dYlAC1J.png">
    <style type='text/css'>
       body { font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
              padding-left: 80px; padding-right: 80px;
       }
       .menuItem { color: #CCFFFF; }
       .heading { color: #FFFF33; margin-top: 10px; margin-bottom: 10px; }
       .pageHeading { color: #990033; text-align: center; }
       .center-align { text-align: center; }
       .archiveArrows { width: 30px; margin-left: 5px; }
       .tweetField { padding-left: 15px; }
       .statField { color:#990033; font-weight: bold; font-size: 7pt; margin-left: 575px; padding-top: 15px; }
       .statIcon { margin-left: 5px; width: 15px; }
       .trendLinks { color: #CCFFFF; font-size: 9pt;}
       a { color: #990033; text-decoration:none; }
       table { font-size: 10pt; }
       ul { margin-right: 30px; }
       #menu { width: 150px; background-color: #990033; text-align: center; padding:10px; }
       #homeName { color: #CCFFFF; font-style: italic; }
       #tweets { width: 900px; background-color: #CCFFFF; padding: 10px; }
       #homeImage{ padding-right:15px; width:100px; }
       #trends { margin-left: 20px; }
       .menuOptions {list-style: none; width: 100px; font-size: 9pt; }
       #timelineLink { color: #CCFFFF; }
       #deleteIcon { width: 20px; margin-left: 10px; }
       #date { margin-left: 550px; color:#990033; font-weight: bold; font-size: 7pt; }
       #userField { padding-left: 15px; font-weight: bold;}
       #userHandle { padding-left: 5px; font-size: 9pt; }
       #logout { font-weight: bold; }
       #logoutIcon { margin-left: 670px; width: 15px; padding-right: 5px;}
       input[type="text"] { border-radius: 10px; outline: none; }
       input[type="submit"] {
            width: 65px;
            margin-top: 10px;
            margin-bottom: 10px;
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

    </style>
    
  </head>
  
  <body>
		 <table>
		 <tr valign='top'>
		     <td id="menu">{{!menu}}</td>
		     <td id="tweets">
		     <a id = 'logout' href='/logout'>
		     <img id ='logoutIcon' title = 'Logout' src='https://cdn4.iconfinder.com/data/icons/cc_mono_icon_set/blacks/48x48/on-off.png' />
		     Logout</a><h1 class = "pageHeading">{{!heading}}</h1>
		     {{!html}}</td>
		 </tr>
		 </table>   
  </body>
</html>
​
