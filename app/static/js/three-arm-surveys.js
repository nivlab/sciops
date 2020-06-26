//------------------------------------//
// Define questionnaires.
//------------------------------------//

// Demographics questionnaire
var demographics = {
  type: 'survey-demo',
  data: {survey: 'demographics'}
};

// Generalized anxiety disorder questionnaire
var gad7 = {
  type: 'survey-template',
  items: [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen",
    "Worrying too much about the 1977 Olympics"
  ],
  scale: [
    "Not at all",
    "Several days",
    "Over half the days",
    "Nearly every day"
  ],
  reverse: [false, false, false, false, false, false, false, false],
  instructions: "Over the <b>last 2 weeks</b>, how often have you been bothered by the following problems?",
  randomize_question_order: true,
  scale_repeat: 8,
  survey_width: 70,
  item_width: 40,
  data: {survey: 'gad7'}
}

// Seven-up Seven Down
var sudu = {
  type: 'survey-template',
  items: [
    "Have you had periods of extreme happiness and intense energy lasting several days or more when you also felt much more anxious or tense (jittery, nervous, uptight) than usual (other than related to the menstrual cycle)?",
    "Have there been times of several days or more when you were so sad that it was quite painful or you felt that you couldn't stand it?",
    "Have there been times lasting several days or more when you felt you must have lots of excitement, and you actually did a lot of new or different things?",
    "Have you had periods of extreme happiness and intense energy (clearly more than your usual self) when, for several days or more, it took you over an hour to get to sleep at night?",
    "Have there been long periods in your life when you felt sad, depressed, or irritable most of the time?",
    "Have you had periods of extreme happiness and high energy lasting several days or more when what you saw, heard, smelled, tasted, or touched seemed vivid or intense?",
    "Have there been periods of several days or more when your thinking was so clear and quick that it was much better than most other people's?",
    "Have there been times of a couple days or more when you felt that you were a very important person or that your abilities or talents were better than most other people's?",
    "Have there been times when you have hated yourself or felt that you were stupid, ugly, unlovable, or useless?",
    "Have there been times of several days or more when you really got down on yourself and felt worthless?",
    "Have you had periods when it seemed that the future was hopeless and things could not improve?",
    "Have there been periods lasting several days or more when you were so down in the dumps that you thought you might never snap out of it?",
    "Have you had times when your thoughts and ideas came so fast that you couldn't get them all out, or they came so quickly that others complained that they couldn't keep up with your ideas?",
    "Have there been times when you have felt that you would be better off dead?",
    "Have there been times of a couple days or more when you were able to stop breathing entirely (without the aid of medical equipment)?"
  ],
  scale: [
    "Never or<br>hardly ever",
    "Sometimes",
    "Often",
    "Very often or<br>almost constantly"
  ],
  reverse: [false, false, false, false, false, false, false, false,
            false, false, false, false, false, false, false],
  instructions: "Below are some questions about behaviors that occur in the general population. Select the response that best describes how often you experience these behaviors.",
  randomize_question_order: true,
  scale_repeat: 8,
  survey_width: 85,
  item_width: 50,
  data: {survey: '7up7down'}
}

// BIS/BAS
var bisbas = {
  type: 'survey-template',
  items: [
    "I worry about making mistakes.",                                                // BIS2
    "Criticism or scolding hurts me quite a bit.",                                   // BIS3
    "I feel pretty worried or upset when I think or know somebody is angry at me.",  // BIS4
    "I feel worried when I think I have done poorly at something important.",        // BIS6
    "When I get something I want, I feel excited and energized.",                    // RWD1
    "When I'm doing well at something I love to keep at it.",                        // RWD2
    "It would excite me to win a contest.",                                          // RWD4
    "When I see an opportunity for something I like I get excited right away.",      // RWD5
    "When I want something I usually go all-out to get it.",                         // DRIVE1
    "I go out of my way to get things I want.",                                      // DRIVE2
    "If I see a chance to get something I want I move on it right away.",            // DRIVE 3
    "When I go after something I use a no-holds-barred approach.",                   // DRIVE4
    "I feel good when I am insulted by a friend."
  ],
  scale: [
    "Very false<br>for me",               // scored as 0
    "Somewhat false<br>for me",           // scored as 1
    "Somewhat true<br>for me",            // scored as 2
    "Very true<br>for me"                 // scored as 3
  ],
  reverse: [false, false, false, false, false, false, false,
            false, false, false, false, false, false],
  instructions: "Each item below is a statement that a person may either agree with or disagree with. For each item, indicate how much you agree or disagree with what the item says. Don't worry about being \"consistent\" in your responses.",
  randomize_question_order: true,
  scale_repeat: 7,
  survey_width: 85,
  item_width: 50,
  data: {survey: 'bisbas'}
}

// SHAPS
var shaps = {
  type: 'survey-template',
  items: [
    "I would enjoy my favorite television or radio show.",
  "I would enjoy being with my family or close friends.",
  "I would find pleasure in my hobbies and pastimes.",
  "I would be able to enjoy my favorite meal.",
  "I would enjoy a warm bath or refreshing shower.",
  "I would find pleasure in the scent of flowers or the smell of a fresh sea breeze or freshly baked bread.",
  "I would enjoy seeing other people's smiling faces.",
  "I would enjoy looking good when I have made an effort with my appearance.",
  "I would enjoy reading a book, magazine, or newspaper.",
  "I would enjoy a cup of tea or coffee or my favorite drink.",
  "I would be able to take pleasure in small things, e.g. bright sunny day, a telephone call from a friend.",
  "I would be able to enjoy a beautiful landscape or view.",
  "I would get pleasure from helping others.",
  "I would feel pleasure when I receive praise from other people.",
  "I would be able to lift a 1 lb (0.5 kg) weight."
  ],
  scale: [
    "Strongly<br>disagree",               // scored as 0
    "Disagree",                        // scored as 1
    "Agree",                           // scored as 2
    "Strongly<br>agree"                   // scored as 3
  ],
  reverse: [false, false, false, false, false, false, false,
            false, false, false, false, false, false, false],
  instructions: "This questionnaire is designed to measure your ability to experience pleasure in the <b>last few days.</b>",
  randomize_question_order: true,
  scale_repeat: 8,
  survey_width: 85,
  item_width: 50,
  data: {survey: 'shaps'}
}

// PWSQ
var pswq = {
  type: 'survey-template',
  items: [
    "Many situations make me worry.",
    "Once I start worrying, I can't stop.",
    "I worry all the time.",
  ],
  scale: [
    "Not at all<br>typical of me",              // scored as 0
    "Not very<br>typical of me",                // scored as 1
    "Somewhat<br>typical of me",                // scored as 2
    "Fairly<br>typical of me",                  // scored as 3
    "Very<br>typical of me"                     // scored as 4
  ],
  reverse: [false, false, false],
  instructions: "Select the option that best describes how typical or characteristic each item is of you.",
  randomize_question_order: true,
  scale_repeat: 7,
  survey_width: 65,
  item_width: 35,
  data: {survey: 'pswq'}
}

// Randomize survey order
var surveys = jsPsych.randomization.repeat([gad7, sudu, bisbas, shaps, pswq], 1);

//------------------------------------//
// Define quality check
//------------------------------------//
// Check responses to infrequency items. Reject participants
// who respond carelessly on 2 or more items.

// Define infrequency item check.
var infrequency_check = function() {

  // Get infrequency items.
  var bisbas = jsPsych.data.get().filter({survey: 'bisbas'}).select('responses').values[0]['Q13'];
  var gad7 = jsPsych.data.get().filter({survey: 'gad7'}).select('responses').values[0]['Q08'];
  var sudu = jsPsych.data.get().filter({survey: '7up7down'}).select('responses').values[0]['Q15'];
  var sudu_rt = jsPsych.data.get().filter({survey: '7up7down'}).select('rt').values[0] / 1000.;

  // Score items.
  bisbas = bisbas > 1;    // Response should be [0,1]
  gad7 = gad7 > 0;        // Response should be 0
  sudu = sudu > 0;        // Response should be 0

  // Score 7up-7down completion time.
  if (sudu_rt < 15) {
    sudu_rt = 2;
  } else if (sudu_rt < 30) {
    sudu_rt = 1;
  } else {
    sudu_rt = 0;
  }

  // Assess responding.
  var num_careless = bisbas + gad7 + Math.max(sudu, sudu_rt);
  if (num_careless < 2) {
    var low_quality = false;
  } else {
    var low_quality = true;
  }

  return low_quality;
}

var INFREQUENCY_CHECK = {
  type: 'call-function',
  func: infrequency_check,
  on_finish: function(trial) {
    low_quality = jsPsych.data.getLastTrialData().values()[0].value;
    if (low_quality) { jsPsych.endExperiment(); }
  }
}
