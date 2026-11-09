/* Inhalte: Farben, Vorlagen, Rituale, Reisen, Sprüche */

const COLORS = ['#FF6B6B', '#FF9F43', '#F2B42B', '#1DD1A1', '#10AC84', '#3CC2E0',
  '#2E86DE', '#5F27CD', '#A55EEA', '#FF6B9D', '#64708A', '#00B894'];

const EMOJIS = ['⭐️', '💧', '🧘', '📚', '🏃', '👟', '☀️', '🍎', '🥗', '💪', '🛌', '✍️',
  '🎯', '💰', '🧹', '🎸', '🚭', '🍬', '📵', '🙏', '🧠', '❤️', '🌱', '☕️',
  '🥣', '🤸', '🍵', '⏰', '📝', '🌬️', '🚶', '🦷', '💊', '🧴', '🎨', '🗣️'];

const RITUAL_EMOJIS = ['🌅', '☀️', '🌙', '🌤️', '🏋️', '💼', '🍽️', '📚', '🧘', '🛁', '⭐️', '🌿'];

const THEMES = {
  morning: { name: 'Sonnenaufgang', a: '#FFB457', b: '#EE5A36' },
  afternoon: { name: 'Mittagshimmel', a: '#3CC2C9', b: '#2B70C9' },
  evening: { name: 'Nacht', a: '#5B4FC4', b: '#211B5C' },
  forest: { name: 'Wald', a: '#3DBE8B', b: '#13705A' },
  rose: { name: 'Rose', a: '#FF8FB1', b: '#C93D66' },
  slate: { name: 'Schiefer', a: '#8290AE', b: '#384260' },
};

const SLOTS = {
  morning: { name: 'Morgenritual', emoji: '🌅', theme: 'morning', time: '07:00' },
  afternoon: { name: 'Nachmittagsritual', emoji: '☀️', theme: 'afternoon', time: '13:00' },
  evening: { name: 'Abendritual', emoji: '🌙', theme: 'evening', time: '21:30' },
};

const TEMPLATES = [
  { title: 'Wasser trinken', emoji: '💧', color: '#3CC2E0', kind: 'count', freq: 'daily', target: 8, unit: 'Gläser', step: 1 },
  { title: 'Meditieren', emoji: '🧘', color: '#A55EEA', kind: 'check', freq: 'daily', target: 1, duration: 5 },
  { title: 'Lesen', emoji: '📚', color: '#FF9F43', kind: 'count', freq: 'daily', target: 20, unit: 'Seiten', step: 5 },
  { title: 'Sport', emoji: '🏃', color: '#1DD1A1', kind: 'check', freq: 'weekly', target: 3 },
  { title: 'Schritte', emoji: '👟', color: '#2E86DE', kind: 'count', freq: 'daily', target: 10000, unit: 'Schritte', step: 1000 },
  { title: 'Früh aufstehen', emoji: '⏰', color: '#F2B42B', kind: 'check', freq: 'daily', target: 1 },
  { title: 'Kein Zucker', emoji: '🍬', color: '#FF6B9D', kind: 'check', freq: 'daily', target: 1 },
  { title: 'Tagebuch', emoji: '✍️', color: '#64708A', kind: 'check', freq: 'daily', target: 1, duration: 5 },
  { title: 'Sparen', emoji: '💰', color: '#10AC84', kind: 'count', freq: 'weekly', target: 50, unit: '€', step: 5 },
  { title: 'Zahnseide', emoji: '🦷', color: '#00B894', kind: 'check', freq: 'daily', target: 1, duration: 2 },
];

const QUOTES = [
  'Kleine Schritte führen zu großen Zielen.',
  'Fortschritt schlägt Perfektion.',
  'Du musst nicht perfekt sein. Bleib einfach dran.',
  'Heute ist ein guter Tag, um anzufangen.',
  'Gewohnheiten formen, wer du wirst.',
  'Jeder Haken zählt.',
  'Ein bisschen jeden Tag ist mehr als viel ab und zu.',
  'Was du heute tust, macht morgen leichter.',
];

const hb = (title, emoji, color, minutes, slot, tip) => ({ title, emoji, color, minutes, slot, tip });

const JOURNEYS = [
  {
    id: 'energy', title: 'Energie für jeden Tag', subtitle: 'Starte wacher und fitter in deine Tage',
    emoji: '⚡️', theme: 'morning',
    steps: [
      { id: 'energy-1', title: 'Der erste Schritt', kind: 'task', action: 'Ich bin bereit', text:
`Schön, dass du hier bist.

Große Veränderungen entstehen selten über Nacht. Sie entstehen aus kleinen Dingen, die du jeden Tag wiederholst. So klein, dass du kaum scheitern kannst.

Auf dieser Reise baust du dir Schritt für Schritt ein Morgenritual auf, das dir Energie gibt. Jede Etappe bringt eine neue Gewohnheit. Erst wenn sie sitzt, geht es weiter.

Bereit?` },
      { id: 'energy-2', title: 'Ein Glas Wasser', kind: 'habit', days: 3,
        habit: hb('Ein Glas Wasser trinken', '💧', '#3CC2E0', 1, 'morning', 'Stell dir das Glas schon am Abend neben das Bett.'), text:
`Nach einer Nacht ohne Trinken ist dein Körper leicht dehydriert. Genau das macht viele Menschen morgens müde und unkonzentriert.

Deine erste Gewohnheit ist darum ganz einfach: Trink direkt nach dem Aufstehen ein großes Glas Wasser. Stell es dir am besten schon abends neben das Bett.` },
      { id: 'energy-3', title: 'Warum willst du das?', kind: 'task', action: 'Aufgeschrieben', text:
`Gewohnheiten halten länger, wenn du weißt, wofür du sie machst.

Nimm dir zwei Minuten und schreib auf: Was würdest du mit mehr Energie anfangen? Mehr Zeit mit Freunden? Endlich Sport? Konzentrierter arbeiten?

Trag deine Antwort bei einer deiner Gewohnheiten unter „Tipp / Motivation“ ein. Dann siehst du sie jedes Mal wieder.` },
      { id: 'energy-4', title: 'Ein gutes Frühstück', kind: 'habit', days: 3,
        habit: hb('Gesund frühstücken', '🥣', '#F2B42B', 10, 'morning', 'Bereite am Abend vorher schon etwas vor.'), text:
`Ein ausgewogenes Frühstück mit etwas Eiweiß und Ballaststoffen hält deinen Blutzucker stabil. Und damit auch deine Laune und Konzentration.

Es muss nicht aufwendig sein: Haferflocken mit Obst, ein Joghurt mit Nüssen oder ein Vollkornbrot reichen völlig.` },
      { id: 'energy-5', title: 'Kurz bewegen', kind: 'habit', days: 5,
        habit: hb('5 Minuten Bewegung', '🤸', '#1DD1A1', 5, 'morning', 'Leg deine Lieblingsmusik dazu auf.'), text:
`Schon fünf Minuten Bewegung bringen deinen Kreislauf in Schwung: Hampelmänner, ein paar Kniebeugen, Dehnen oder einmal um den Block.

Wichtig ist nicht, wie viel du machst. Wichtig ist, dass du es jeden Morgen machst.` },
      { id: 'energy-6', title: 'Geschafft!', kind: 'letter', text:
`Schau, wie weit du gekommen bist: Dein Morgenritual besteht jetzt aus drei Gewohnheiten, die dir jeden Tag Energie schenken.

Gönn dir einen Moment Stolz. Und dann such dir deine nächste Reise aus.` },
    ],
  },
  {
    id: 'sleep', title: 'Besser schlafen', subtitle: 'Ruhiger einschlafen, erholter aufwachen',
    emoji: '🌙', theme: 'evening',
    steps: [
      { id: 'sleep-1', title: 'Schlaf ist deine Superkraft', kind: 'task', action: 'Los geht’s', text:
`Guter Schlaf ist die Grundlage für fast alles: Laune, Konzentration, Gesundheit.

Auf dieser Reise baust du dir ein Abendritual, das deinem Körper signalisiert: Jetzt ist Zeit zum Runterfahren.` },
      { id: 'sleep-2', title: 'Bildschirme aus', kind: 'habit', days: 3,
        habit: hb('Handy weglegen', '📵', '#64708A', 1, 'evening', 'Ein normaler Wecker statt Handy hilft enorm.'), text:
`Helles Licht und ständige Reize halten dein Gehirn wach. Leg dein Handy 30 Minuten vor dem Schlafen weg, am besten außerhalb des Schlafzimmers.` },
      { id: 'sleep-3', title: 'Dein Schlafzimmer', kind: 'task', action: 'Erledigt', text:
`Dunkel, ruhig und eher kühl (ca. 18 °C): So schläft es sich am besten. Lüfte heute einmal richtig durch und schau, was dich beim Einschlafen stört.` },
      { id: 'sleep-4', title: 'Runterkommen', kind: 'habit', days: 3,
        habit: hb('Tee & Lesen', '🍵', '#A55EEA', 15, 'evening', 'Am besten ein Papierbuch, kein Bildschirm.'), text:
`Ein festes kleines Ritual hilft beim Abschalten: ein Kräutertee, ein paar Seiten in einem Buch oder ruhige Musik.` },
      { id: 'sleep-5', title: 'Feste Aufstehzeit', kind: 'habit', days: 5,
        habit: hb('Pünktlich aufstehen', '⏰', '#FF6B6B', 1, 'morning', 'Kein Snooze. Sofort aufstehen.'), text:
`Dein innerer Rhythmus liebt Regelmäßigkeit. Steh jeden Tag zur gleichen Zeit auf, auch am Wochenende, so gut es geht.` },
      { id: 'sleep-6', title: 'Gute Nacht', kind: 'letter', text:
`Du hast dir ein richtiges Abendritual aufgebaut. Bleib dran. Guter Schlaf wird mit jeder Woche selbstverständlicher.` },
    ],
  },
  {
    id: 'focus', title: 'Fokus & Klarheit', subtitle: 'Weniger Ablenkung, mehr geschafft',
    emoji: '🎯', theme: 'afternoon',
    steps: [
      { id: 'focus-1', title: 'Weniger, aber besser', kind: 'task', action: 'Verstanden', text:
`Produktiv zu sein heißt nicht, mehr zu machen. Es heißt, das Richtige zu machen. Auf dieser Reise lernst du, deine Aufmerksamkeit zu schützen.` },
      { id: 'focus-2', title: 'Deine Top 3', kind: 'habit', days: 3,
        habit: hb('Top 3 des Tages planen', '📝', '#2E86DE', 5, 'morning', 'Die wichtigste Aufgabe zuerst erledigen.'), text:
`Schreib jeden Morgen die drei wichtigsten Dinge des Tages auf. Wenn du nur diese drei schaffst, war der Tag ein Erfolg.` },
      { id: 'focus-3', title: 'Benachrichtigungen aufräumen', kind: 'task', action: 'Aufgeräumt', text:
`Jede Benachrichtigung reißt dich raus. Geh heute durch deine Einstellungen und schalte alles aus, was nicht wirklich wichtig ist.` },
      { id: 'focus-4', title: 'Fokuszeit', kind: 'habit', days: 3,
        habit: hb('Fokuszeit ohne Handy', '🧠', '#5F27CD', 25, 'afternoon', 'Handy in einen anderen Raum legen.'), text:
`Arbeite 25 Minuten an einer einzigen Sache, das Handy außer Reichweite. Danach 5 Minuten Pause. Der Timer im Ritual-Modus hilft dir dabei.` },
      { id: 'focus-5', title: 'Den Tag abschließen', kind: 'habit', days: 5,
        habit: hb('Tag reflektieren', '✍️', '#64708A', 5, 'evening', 'Was lief heute gut? Drei Sätze reichen.'), text:
`Schau abends kurz zurück: Was lief gut? Was nimmst du mit? So wird dein Kopf frei für den Feierabend.` },
      { id: 'focus-6', title: 'Klarer Kopf', kind: 'letter', text:
`Du planst, du fokussierst, du reflektierst. Damit hast du ein System, das dich jeden Tag ein Stück weiterbringt.` },
    ],
  },
  {
    id: 'calm', title: 'Ruhe & Achtsamkeit', subtitle: 'Weniger Stress, mehr Gelassenheit',
    emoji: '🧘', theme: 'forest',
    steps: [
      { id: 'calm-1', title: 'Innehalten', kind: 'task', action: 'Ich bin dabei', text:
`Stress lässt sich nicht immer vermeiden. Aber du kannst lernen, anders damit umzugehen. Diese Reise schenkt dir jeden Tag kleine Momente der Ruhe.` },
      { id: 'calm-2', title: 'Meditation', kind: 'habit', days: 3,
        habit: hb('Meditieren', '🧘', '#1DD1A1', 5, 'morning', 'Gleicher Ort, gleiche Zeit.'), text:
`Setz dich bequem hin, schließ die Augen und beobachte fünf Minuten lang deinen Atem. Wenn Gedanken kommen, lass sie ziehen und kehr zum Atem zurück.` },
      { id: 'calm-3', title: 'Dankbarkeit', kind: 'habit', days: 3,
        habit: hb('Dankbarkeit notieren', '🙏', '#FF6B9D', 3, 'evening', 'Auch Kleinigkeiten zählen.'), text:
`Schreib jeden Abend drei Dinge auf, für die du heute dankbar bist. Das lenkt den Blick auf das, was gut läuft.` },
      { id: 'calm-4', title: 'Ein Spaziergang', kind: 'task', action: 'Gemacht', text:
`Geh heute 15 Minuten spazieren, ohne Handy und ohne Kopfhörer. Achte nur auf das, was du siehst, hörst und riechst.` },
      { id: 'calm-5', title: 'Atempause', kind: 'habit', days: 5,
        habit: hb('Tief durchatmen', '🌬️', '#3CC2E0', 2, 'afternoon', 'Länger aus- als einatmen.'), text:
`Mitten am Tag: Atme 4 Sekunden ein, halte 4 Sekunden, atme 6 Sekunden aus. Zwei Minuten reichen, um dein Nervensystem zu beruhigen.` },
      { id: 'calm-6', title: 'Gelassenheit', kind: 'letter', text:
`Morgens, mittags und abends hast du jetzt einen ruhigen Moment für dich. Das ist ein Geschenk, das du dir jeden Tag selbst machst.` },
    ],
  },
];
