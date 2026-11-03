import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { ProTip } from "./challenge-view";

describe("ProTip", () => {
  it("renders the Pro tip label with the takeaway text", () => {
    const html = renderToStaticMarkup(
      <ProTip text="Cache reads are ~10x cheaper than re-reading fresh input." />,
    );
    expect(html).toContain("Pro tip");
    expect(html).toContain("Cache reads are ~10x cheaper than re-reading fresh input.");
  });

  it("renders in the green callout styling so it is not skippable", () => {
    const html = renderToStaticMarkup(<ProTip text="Model choice is a cost lever." />);
    expect(html).toContain("bg-green-50");
    expect(html).toContain("text-green-700");
  });
});
