type WordForm = {
  label: string;
  forms: string[];
  number?: string;
  definiteness?: string;
  gender?: string;
  degree?: string;
  tense?: string;
};

export default function WordFormTable({ forms }: { forms: WordForm[] }) {
  return (
    <table className="w-full border-collapse rounded-lg overflow-hidden shadow">
      <thead>
        <tr className="bg-gray-100 text-left">
          <th className="p-2 font-semibold w-1/3">Label</th>
          <th className="p-2 font-semibold w-1/3">Forms</th>
          <th className="p-2 font-semibold w-1/3">Metadata</th>
        </tr>
      </thead>
      <tbody>
        {forms.map((form, i) => (
          <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
            <td className="p-2 font-medium">{form.label}</td>
            <td className="p-2">
              {form.forms.map((f, idx) =>
                ["å", "har"].includes(f) ? (
                  <span key={f + idx}>
                    {idx > 0 && "; "}
                    <em>{f}</em>
                  </span>
                ) : (
                  <span key={f + idx}>
                    {idx > 0 && "; "}
                    {f}
                  </span>
                )
              )}
            </td>
            <td className="p-2 text-sm text-gray-600">
              {[form.number && `Number: ${form.number}`,
                form.gender && `Gender: ${form.gender}`,
                form.definiteness && `Definiteness: ${form.definiteness}`,
                form.degree && `Degree: ${form.degree}`,
                form.tense && `Tense: ${form.tense}`]
                .filter(Boolean)
                .join(" • ")}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
