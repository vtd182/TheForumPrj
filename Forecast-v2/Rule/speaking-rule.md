IELTS_SPEAKING_AGENT_RULES:
  target_band: 7_plus
  scoring_criteria:
    - fluency_and_coherence
    - lexical_resource
    - grammatical_range_and_accuracy
    - pronunciation

  global_rules:
    - Script must sound spoken, not essay-like.
    - Do not create memorized-sounding answers.
    - Every answer must directly answer the question first.
    - Extend ideas coherently with examples, reasons, contrasts, or consequences.
    - Use natural discourse markers, but do not overuse them.
    - Include paraphrase instead of repeating the question words too much.
    - Use topic-specific vocabulary, collocations, and some idiomatic language naturally.
    - Mix simple, compound, and complex sentences.
    - Avoid grammar so complex that it creates unnatural or error-prone speech.
    - Add pronunciation guidance only as speakable cues: chunking, stress, pausing, intonation.
    - Maintain clarity over impressiveness.

  band_9_rules:
    fluency:
      - Almost no repetition or self-correction.
      - Hesitation only for content planning, not word/grammar searching.
      - Fully coherent, appropriately extended topic development.
    vocabulary:
      - Precise, flexible, idiomatic language in all contexts.
    grammar:
      - Precise and accurate structures almost all the time.
    pronunciation:
      - Full phonological range, effortless intelligibility, accent does not affect clarity.

  band_8_rules:
    fluency:
      - Very occasional repetition/self-correction.
      - Mostly content-related hesitation.
      - Coherent, relevant topic development.
    vocabulary:
      - Wide, flexible vocabulary.
      - Less common/idiomatic items allowed, with rare collocation issues.
      - Effective paraphrase.
    grammar:
      - Wide range of structures.
      - Most sentences error-free; occasional non-systematic errors acceptable.
    pronunciation:
      - Wide phonological range.
      - Rhythm, stress, and intonation sustained with occasional lapses.
      - Easily understood.

  band_7_rules:
    fluency:
      - Can produce long turns without noticeable effort.
      - Some hesitation/repetition/self-correction is acceptable if coherence is not harmed.
      - Flexible discourse markers and cohesive features.
    vocabulary:
      - Flexible vocabulary for varied topics.
      - Some less common/idiomatic language.
      - Awareness of style and collocation.
      - Effective paraphrase.
    grammar:
      - Frequent error-free sentences.
      - Both simple and complex sentences used effectively.
      - Some errors acceptable; a few basic errors may persist.
    pronunciation:
      - Must show all positive band 6 pronunciation features plus some band 8 features.

  avoid_band_6_or_below:
    - Do not rely on basic vocabulary only.
    - Do not overuse linking words like "firstly", "secondly", "moreover" in every answer.
    - Do not make answers too short or repetitive.
    - Do not create frequent grammar errors in complex sentences.
    - Do not make the script sound slow, hesitant, or word-searching.
    - Do not use unnatural idioms just to sound advanced.
    - Do not write Part 2 as a memorized essay.

  part_1_script_rules:
    answer_length: "2-4 sentences"
    structure:
      - direct_answer
      - brief_reason_or_detail
      - optional_example_or_contrast
    style:
      - conversational
      - personal
      - concise
    must_include:
      - natural paraphrase
      - at least one specific detail
    avoid:
      - long essay-style answer
      - overexplaining simple questions

  part_2_script_rules:
    answer_length: "90-120 seconds spoken"
    structure:
      - opening_context
      - main story/details
      - feelings/opinion
      - short reflective ending
    style:
      - narrative
      - coherent sequencing
      - extended but natural
    must_include:
      - natural spoken fillers (e.g., "To be honest...", "Well, off the top of my head...")
      - time/place/person/object details where relevant
      - varied tense usage when natural
      - cohesive sequencing phrases
      - topic vocabulary
    avoid:
      - bullet-point sounding delivery
      - memorized template phrases
      - too many rare words

  part_3_script_rules:
    answer_length: "4-7 sentences"
    structure:
      - clear opinion/general answer
      - explanation
      - example or comparison
      - nuance/counterpoint/result
    style:
      - analytical
      - abstract/generalized
      - balanced
    must_include:
      - cause-effect language
      - comparison/contrast where useful
      - precise vocabulary
      - complex sentence forms
    avoid:
      - only personal examples
      - simplistic yes/no answers
      - unsupported opinions

  response_generation_checklist:
    fluency_check:
      - Is the answer easy to say aloud?
      - Are pauses natural and content-based?
      - Is the idea development coherent?
    vocabulary_check:
      - Are there natural collocations?
      - Is there paraphrase?
      - Are idioms used only when appropriate?
    grammar_check:
      - Is there a mix of simple and complex grammar?
      - Are complex sentences controlled?
    pronunciation_check:
      - Can the script be chunked naturally?
      - Are key words easy to stress?
      - Is the rhythm conversational?

  agent_instruction:
    - For every IELTS Speaking answer, optimize for Band 7-8 unless user requests otherwise.
    - Prioritize coherence, naturalness, and clarity before advanced vocabulary.
    - Add optional pronunciation notes after the script using slash chunks and stress hints.