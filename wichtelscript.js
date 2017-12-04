

function shuffle(array)
{
  var currentTime = new Date();
  Math.seed = currentTime.getFullYear();

  // in order to work 'Math.seed' must NOT be undefined,
  // so in any case, you HAVE to provide a Math.seed
  Math.seededRandom = function(max, min)
  {
    max = max || 1;
    min = min || 0;

    Math.seed = (Math.seed * 9301 + 49297) % 233280;
    var rnd = Math.seed / 233280;

    return min + rnd * (max - min);
  }
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex)
  {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.seededRandom() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

function CheckName(name,array)
{
  for(i = 0; i<array.length; i++)
  {
    if(name == array[i])
    {
      return i;
    }
  }
}
var ListOfNames = [	"Ursula",
                    "Claudia",
                    "Lutz",
                    "Kerstin",
                    "Jens",
                    "Stefan",
                    "Lydia",
                    "Marie",
                    "Nico",
                    "Jane",
                    "Timo",
                    "Lukas",
                    "Madi",
                    "Lina",
                    "Kacper"]

var CodeName = [    "U78xk",
                    "Ckl2s",
                    "Lpo2k",
                    "K23k0",
                    "J2300",
                    "Sj3ql",
                    "Lalk3",
                    "Ma2kj",
                    "N2w3n",
                    "J3nn5",
                    "T09if",
                    "Lna3j",
                    "M78sd",
                    "Lbn43",
                    "Knf09",
                  ]

alert( 'Wilkommen beim Wichtelprogramm 2017' );


  var pw = prompt("Gib bitte dein Passwort ein", "Dein Passwort");
  var UName = null;
  UName = CheckName(pw,CodeName);

  var customerName = ListOfNames[UName]
  var pick = null
  pick = CheckName(customerName,ListOfNames);
  if(pick == null)
  {
    alert('Falsches Passwort! Wende dich ggf. an Lukas oder ueberpruefe deine Email!')
  }
  else
  {
    shuffle(ListOfNames)

    alert('Dein_e Wichterpartner_in ist '+ ListOfNames[pick])
  }
  //alert(ListOfNames)
