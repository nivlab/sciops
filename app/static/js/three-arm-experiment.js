//------------------------------------//
// Define parameters.
//------------------------------------//

// Define context (color) assignment.
const contexts = jsPsych.randomization.shuffle(['red','green','blue']);

// Define choices.
const choices = [37,38,39];    // left, top, right

// Define timings.
const choice_duration = 10000;
const feedback_duration = 1200;

// Define comprehension threshold.
var max_errors = 0;
var max_loops = 2;
var num_loops = 0;

// Define missed repsonses count.
var missed_threshold = 6;
var missed_responses = 0;

//------------------------------------//
// Define images to preload.
//------------------------------------//

preload_images = [
  "../static/img/cloud01.svg",
  "../static/img/cloud02.svg",
  "../static/img/cloud03.svg",
  "../static/img/animal-fish01.svg",
  "../static/img/animal-tire.svg",
  "../static/img/animal-lion.svg",
  "../static/img/animal-snake.svg",
  "../static/img/surfboard-blue.svg",
  "../static/img/surfboard-green.svg",
  "../static/img/surfboard-red.svg",
  "../static/img/instructions01.png",
  "../static/img/instructions02.png",
  "../static/img/instructions03.png",
  "../static/img/instructions04.png",
  "../static/img/instructions05.png",
  "../static/img/instructions06.png",
  "../static/img/instructions07.png",
  "../static/img/instructions08.png",
  "../static/img/instructions09.png",
];

//------------------------------------//
// Define instructions block.
//------------------------------------//

// Define image scaling CSS.
const style = "width:auto; height:auto; max-width:100%; max-height:80vh;";

// Define instructions sequence.
var instructions = {
  type: 'instructions',
  pages: [
    `<img src='../static/img/instructions01.png' style="${style}"</img>`,
    `<img src='../static/img/instructions02.png' style="${style}"</img>`,
    `<img src='../static/img/instructions03.png' style="${style}"</img>`,
    `<img src='../static/img/instructions04.png' style="${style}"</img>`,
    `<img src='../static/img/instructions05.png' style="${style}"</img>`,
    `<img src='../static/img/instructions06.png' style="${style}"</img>`,
    `<img src='../static/img/instructions07.png' style="${style}"</img>`,
    `<img src='../static/img/instructions08.png' style="${style}"</img>`,
  ],
  show_clickable_nav: true,
  button_label_previous: "Prev",
  button_label_next: "Next"
}

// Define comprehension check.
var comprehension = {
  type: 'three-arm-comprehension'
}

// Define instructions loop.
var instructions_loop = {
  timeline: [
    instructions,
    comprehension
  ],
  loop_function: function(data) {

    // Extract number of errors.
    const num_errors = data.values().slice(-1)[0].num_errors;

    // Check if instructions should repeat.
    if (num_errors > max_errors) {
      num_loops++;
      return true;
    } else {
      return false;
    }

  }
}

var comprehension_check = {
  type: 'call-function',
  func: function(){},
  on_finish: function(trial) {
    if (low_quality) { jsPsych.endExperiment(); }
  }
}

// Define ready check.
var ready = {
  type: 'instructions',
  pages: [
    `<img src='../static/img/instructions09.png' style="${style}"</img>`,
  ],
  show_clickable_nav: true,
  button_label_previous: "Prev",
  button_label_next: "Next"
}

//------------------------------------//
// Define 3-arm bandit task.
//------------------------------------//

// Define rotate function.
function arrayRotate(arr, reverse) {
  if (reverse) arr.unshift(arr.pop());
  else arr.push(arr.shift());
  return arr;
}

// Preallocate space
var blocks = [15, 15, 15, 15, 15, 15];    // number of trials
var probs  = [];
var outcomes = [];
var correct = [];

for (var i = 0; i < blocks.length; i++) {

  // Define reward probabilities for block
  if (i==0) {
    probs.push(jsPsych.randomization.shuffle([0.8, 0.2, 0.2]));
  } else if (Math.random() > 0.5) {
    probs.push(arrayRotate(probs[i-1].slice(), true));
  } else {
    probs.push(arrayRotate(probs[i-1].slice(), false));
  }

  // Iteratively generate outcomes.
  for (var j = 0; j < blocks[i]; j++) {

    // Store correct choice.
    correct.push( probs[i].reduce((iMax, x, i, arr) => x > arr[iMax] ? i : iMax, 0) );

    // Simulate outcomes.
    var trio = [];
    for (var k = 0; k < probs[i].length; k++) {
      trio.push(Math.random() < probs[i][k] ? 1 : 0);
    }
    outcomes.push(trio);

  }

}

// Iteratively define trials.
var trials = [];

for (i = 0; i < outcomes.length; i++) {

  // Define trial.
  const trial = {
    type: 'three-arm-trial',
    contexts: contexts,
    outcomes: outcomes[i],
    choices: choices,
    choice_duration: choice_duration,
    feedback_duration: feedback_duration,
    data: { trial: i+1, correct: correct[i] },
    on_finish: function(data) {

      // Evaluate missing data
      if ( data.key == null ) {

        // Set missing data to true.
        data.missing = true;

      } else {

        // Set missing data to false.
        data.missing = false;

        // Define accuracy.
        data.accuracy = (data.choice == data.correct ? 1 : 0);

      }

    }

  }

  // Define looping node.
  const trial_node = {
    timeline: [trial],
    loop_function: function(data) {
      return data.values()[0].missing;
    }
  }

  // Push trial.
  trials.push(trial_node);

}

//------------------------------------//
// Define feedback screen.
//------------------------------------//

// Define feedback screen.
var feedback = {
  stimulus: '',
  type: 'html-keyboard-response',
  on_start: function(trial) {

    // Compute overall accuracy.
    var accuracy = jsPsych.data.get().filter({trial_type: 'three-arm-trial'}).select('accuracy');
    var accuracy = accuracy.mean();

    // Compute overall points.
    var total = jsPsych.data.get().filter({trial_type: 'three-arm-trial'}).select('outcome');
    var total = total.sum();

    // Report accuracy to subject.
    trial.stimulus = `Points: ${total}<br><br>Accuracy: ${accuracy}<br><br>Press any key to complete the experiment.`

  }
}
