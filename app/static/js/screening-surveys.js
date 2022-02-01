//------------------------------------//
// Define transition screens.
//------------------------------------//

// Welcome screen
var WELCOME = {
  type: 'instructions',
  pages: [
    "<b>Welcome to the study!</b><br><br>We will now get started with some surveys.<br>Please read each survey carefully and respond truthfully."
  ],
  show_clickable_nav: true,
  button_label_previous: 'Prev',
  button_label_next: 'Next',
  on_finish: function(trial) {
    pass_message('starting surveys');
  }
}

//------------------------------------//
// Define questionnaires.
//------------------------------------//

// Demographics questionnaire
var DEMO = {
  type: 'survey-demo',
  data: {survey: 'demographics'}
};

var seven_up = {
  type: 'survey-template',
  items: [

    // Hypomania subscale
    "Have you had periods of extreme happiness and intense energy lasting several days or more when you also felt much more anxious or tense (jittery, nervous, uptight) than usual (other than related to the menstrual cycle)?",
    "Have there been times lasting several days or more when you felt you must have lots of excitement, and you actually did a lot of new or different things?",
    "Have you had periods of extreme happiness and intense energy (clearly more than your usual self) when, for several days or more, it took you over an hour to get to sleep at night?",
    "Have there been times of a couple days or more when you felt that you were a very important person or that your abilities or talents were better than most other people's?",
    "Have you had periods of extreme happiness and high energy lasting several days or more when what you saw, heard, smelled, tasted, or touched seemed vivid or intense?",
    "Have there been periods of several days or more when your thinking was so clear and quick that it was much better than most other people's?",
    "Have you had times when your thoughts and ideas came so fast that you couldn't get them all out, or they came so quickly that others complained that they couldn't keep up with your ideas?",

  ],
  scale: [
    "Never or<br>hardly ever",
    "Sometimes",
    "Often",
    "Very often or<br>almost constantly"
  ],
  reverse: [
    false, false, false, false, false, false, false
  ],
  instructions: 'Below are some questions about behaviors that occur in the general population.<br>Using the scale below, select the number that best describes how often you experience these behaviors.',
  scale_repeat: 7,
  survey_width: 950,
  item_width: 50,
  data: {survey: '7u'},
}

var seven_down = {
  type: 'survey-template',
  items: [

    // Depression subscale
    "Have there been times of several days or more when you were so sad that it was quite painful or you felt that you couldn't stand it?",
    "Have there been long periods in your life when you felt sad, depressed, or irritable most of the time?",
    "Have there been times when you have hated yourself or felt that you were stupid, ugly, unlovable, or useless?",
    "Have there been times of several days or more when you really got down on yourself and felt worthless?",
    "Have you had periods when it seemed that the future was hopeless and things could not improve?",
    "Have there been periods lasting several days or more when you were so down in the dumps that you thought you might never snap out of it?",
    "Have there been times when you have felt that you would be better off dead?"

  ],
  scale: [
    "Never or<br>hardly ever",
    "Sometimes",
    "Often",
    "Very often or<br>almost constantly"
  ],
  reverse: [
    false, false, false, false, false, false, false
  ],
  instructions: 'Below are some questions about behaviors that occur in the general population.<br>Using the scale below, select the number that best describes how often you experience these behaviors.',
  scale_repeat: 7,
  survey_width: 950,
  item_width: 50,
  data: {survey: '7d'},
}

// Penn State Worry Questionnaire
var pswq = {
  type: 'survey-template',
  items: [

    // Worry symptoms
    "My worries overwhelm me.",
    "Many situations make me worry.",
    "I know I should not worry about things, but I just can't help it.",
    "When I'm under pressure I worry a lot.",
    "I'm always worrying about something.",
    "As soon as I finish one task, I start to worry about everything else I have to do.",
    "I have been a worrier all my life.",
    "I notice that I have been worrying about things.",

    // Infrequency item
    "I am usually able to remember my own name."

  ],
  scale: [
    "Not at all<br>typical",
    "Not very<br>typical",
    "Somewhat<br>typical",
    "Fairly<br>typical",
    "Very<br>typical"
  ],
  reverse: [
    false, false, false, false, false, false, false, false, false
  ],
  instructions: 'Select the option that best describes how typical or characteristic each item is of you.',
  survey_width: 950,
  item_width: 40,
  infrequency_items: [8],
  data: {survey: 'pswq'},
  on_finish: function(data) {

    // Score response on infrequncy item.
    const scores = [1,1,1,0.5,0];
    data.infrequency = scores[data.responses['Q09']];

  }

}

// Hexaco artistic interests / creativity
var artistic = {
  type: 'survey-template',
  items: [

    // Hexaco items
    "I believe in the importance of art.",
    "I get deeply immersed in music.",
    "I do not like art.",
    "I have a vivid imagination.",
    "I do not have a good imagination.",
    "I have difficulty imagining things.",

    // Infrequency item
    "I can live for months without any oxygen."

  ],
  scale: [
    "Strongly<br>Disagree",
    "Disagree",
    "Slightly<br>Disagree",
    "Neutral",
    "Slightly<br>Agree",
    "Agree",
    "Strongly<br>Agree"
  ],
  reverse: [false, false, true, false, true, true, false],
  instructions: "The following are some statements about you. Please read each statement and decide<br>how much you agree or disagree with that statement.",
  survey_width: 950,
  item_width: 35,
  infrequency_items: [6],
  data: {survey: 'artistic'},
  on_finish: function(data) {

    // Score response on infrequncy item.
    const scores = [0,0,0,0.5,1,1,1];
    data.infrequency = scores[data.responses['Q07']];

  }
}

// Hexaco greed avoidance
var greed = {
  type: 'survey-template',
  items: [

    // Hexaco items
    "I love luxury.",
    "I have a strong need for power.",
    "I seek status.",
    "I am out for my own personal gain.",
    "I tell other people what they want to hear so that they will do what I want them to do.",
    "I put on a show to impress people.",

    // Infrequency item
    "I have never used a computer."

  ],
  scale: [
    "Strongly<br>Disagree",
    "Disagree",
    "Slightly<br>Disagree",
    "Neutral",
    "Slightly<br>Agree",
    "Agree",
    "Strongly<br>Agree"
  ],
  reverse: [false, false, false, false, false, false, false],
  instructions: "The following are some statements about you. Please read each statement and decide<br>how much you agree or disagree with that statement.",
  survey_width: 950,
  item_width: 35,
  infrequency_items: [6],
  data: {survey: 'greed'},
  on_finish: function(data) {

    // Score response on infrequncy item.
    const scores = [0,0,0,0.5,1,1,1];
    data.infrequency = scores[data.responses['Q07']];

  }
}

//------------------------------------//
// Define survey block
//------------------------------------//

// Define survey block
var SURVEYS = jsPsych.randomization.shuffle([seven_up, seven_down, pswq, artistic, greed]);
