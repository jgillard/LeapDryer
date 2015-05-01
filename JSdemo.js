// Set up the controller:
    Leap.loop({background: true}, {

        hand: function(hand){
                    if (hand.frame.hands.length > 1) {
                      if (hand.type === "left") { return; }
                    }

                  <!-- RPY -->
                  confVal.innerHTML = hand.confidence;
                  outputR.innerHTML = "R ".concat(parseInt(hand.palmNormal[0]*90), &deg);
                  progressR.style.width = 40 + hand.palmNormal[0] * 40 + '%';
                  outputP.innerHTML = "P ".concat(parseInt(hand.direction[1].toPrecision(2)*90), &deg);
                  progressP.style.width = 40 + hand.direction[1] * 40 + '%';
                  outputY.innerHTML = "Y ".concat(parseInt(hand.direction[0].toPrecision(2)*90), &deg);
                  progressY.style.width = 40 + hand.direction[0] * 40 + '%';

                  <!-- XYZ -->
                  outputXX.innerHTML = "X ".concat(-(parseInt(hand.palmPosition[0])));
                  progressXX.style.width = 40 + -(hand.palmPosition[0]) * 0.2 + '%';
                  outputYY.innerHTML = "Y ".concat(parseInt(hand.palmPosition[2]));
                  progressYY.style.width = (hand.palmPosition[2]) * 0.4 + '%';
                  outputZZ.innerHTML = "Z ".concat(parseInt(hand.palmPosition[1]));
                  progressZZ.style.width = hand.palmPosition[1] * 0.2 + '%';
                  
                  <!-- popup text -->
                  /*
                  if (hand.direction[1].toPrecision(2) > -0.55 && hand.direction[1].toPrecision(2) < -0.45) {
                    document.getElementById("DRY").style.visibility="visible";
                  } else {
                    document.getElementById("DRY").style.visibility="hidden";
                  } */

              }
    })

    .use('boneHand', {
      targetEl: document.body,
      arm: true,
      opacity: 0.5
    });