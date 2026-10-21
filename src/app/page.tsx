import { loadHomepage } from "@/lib/config";
import Splash, { type HomepageContent } from "./splash";

export default function Home() {
  const hp = loadHomepage();
  const content: HomepageContent = {
    title: hp.title,
    intro: hp.intro,
    howToPlay: hp.howToPlay,
    cta: hp.cta,
  };
  return <Splash content={content} />;
}
