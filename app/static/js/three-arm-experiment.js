//------------------------------------//
// Define parameters.
//------------------------------------//

// Define context (color) assignment.
const contexts = jsPsych.randomization.shuffle(['red','green','blue']);

// Define choices.
const choices = [37,38,39];    // left, top, right

// Define timings.
// const choice_duration = 10000;
const choice_duration = null;
const feedback_duration = 1500;

// Define comprehension threshold.
const max_errors = 1;

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
      return true;
    } else {
      return false;
    }

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
// Define 2-arm bandit task.
//------------------------------------//

// Define block lengths.
var blocks = jsPsych.randomization.repeat([8, 9, 10, 11, 12], 2, false);
blocks.unshift(12);

// Initialize reward probabilities.
probs = jsPsych.randomization.shuffle([0.7, 0.3, 0.3]);

// Predefine trial outcomes.
var outcomes = [];
var correct = [];

for (var i = 0; i < blocks.length; i++) {

  // Rotate reward probabilities
  if (Math.random() > 0.5) {
    probs.unshift(probs.pop());
  } else {
    probs.push(probs.shift());
  }

  // Iteratively generate outcomes.
  for (var j = 0; j < blocks[i]; j++) {

    // Store correct choice.
    correct.push( probs.reduce((iMax, x, i, arr) => x > arr[iMax] ? i : iMax, 0) )

    // Simulate outcomes.
    const trio = [];
    for (var k = 0; k < probs.length; k++) {
      trio.push(Math.random() > probs[k] ? 1 : 0);
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
    data: { correct: correct[i] + 1 },
    on_finish: function(data) {

      // Evaluate missing data
      if ( data.key == null ) {

        // Set missing data to true.
        data.missing = true;

        // Increment counter. Check if experiment should end.
        missed_responses++;
        if (missed_responses >= missed_threshold) {
          jsPsych.endExperiment();
        }

      } else {

        // Set missing data to false.
        data.missing = false;

        // Define accuracy.
        data.accuracy = data.choice == data.correct;

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
