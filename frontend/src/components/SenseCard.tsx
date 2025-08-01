import WordFormTable from "@/components/WordFormTable";

type Meaning = { description: string; examples?: string[] };
type Expression = { phrase: string; explanation: string };
type WordForm = {
  label: string;
  forms: string[];
  number?: string;
  definiteness?: string;
  gender?: string;
  degree?: string;
  tense?: string;
};

type FlatWordEntry = {
  word: string;
  category?: string;
  gender?: string;
  article?: string;
  meanings?: { description: string; examples?: { sentence: string }[] }[];
  word_forms?: any[];
  expressions?: { phrase: string; explanation: string }[];
};

type Sense = {
  id: string;
  category: string;
  gender?: string;
  article?: string;
  meanings: { description: string; examples?: string[] }[];
  word_forms?: any[];
  expressions?: { phrase: string; explanation: string }[];
};

type WordEntry = FlatWordEntry & { senses?: Sense[] };


export default function SenseCard({ sense }: { sense: Sense }) {
  return (
    <div className="border rounded-lg shadow p-6 bg-white mt-6">
      {/* Sense Header */}
      <div className="mb-4">
        <h3 className="text-2xl font-semibold">{sense.category}</h3>
        <p className="text-gray-700 text-lg">
          {sense.gender && <span className="mr-2">• {sense.gender}</span>}
          {sense.article && <span className="mr-2">• Article: {sense.article}</span>}
        </p>
      </div>

      {/* Meanings */}
      <h4 className="text-lg font-semibold mb-2">Meanings</h4>
      <ol className="list-decimal ml-5 space-y-3">
        {sense.meanings.map((meaning, i) => (
          <li key={i} className="border rounded p-3 bg-gray-50 shadow-sm">
            <p className="font-medium text-gray-800">{meaning.description}</p>
            {meaning.examples && meaning.examples.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-blue-600 text-sm">
                  Show examples ({meaning.examples.length})
                </summary>
                <ul className="list-disc ml-6 mt-2 text-gray-700 text-sm">
                  {meaning.examples.map((ex, j) => (
                    <li key={j}>{ex}</li>
                  ))}
                </ul>
              </details>
            )}
          </li>
        ))}
      </ol>

      {/* Word Forms */}
      {sense.word_forms && sense.word_forms.length > 0 && (
        <div className="mt-6">
          <h4 className="text-lg font-semibold mb-2">Word Forms (Bøyning)</h4>
          <WordFormTable forms={sense.word_forms} />
        </div>
      )}

      {/* Expressions */}
      {sense.expressions && sense.expressions.length > 0 && (
        <div className="mt-6">
          <h4 className="text-lg font-semibold mb-3">Expressions (Faste uttrykk)</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {sense.expressions.map((expr, i) => (
              <div key={i} className="border rounded-lg p-4 bg-gray-50 shadow-sm hover:shadow-md transition">
                <p className="font-medium text-purple-700">{expr.phrase}</p>
                <p className="text-sm text-gray-600 mt-1">{expr.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
