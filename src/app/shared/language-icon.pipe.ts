import { Pipe, PipeTransform } from '@angular/core';

export interface LangMeta {
  icon: string;
  color: string;
  tooltip: string;
}

const LANG_MAP: Record<string, LangMeta> = {
  typescript:  { icon: 'TS',  color: '#3178C6', tooltip: 'TypeScript: JavaScript con tipado estático. Ideal para apps grandes.' },
  javascript:  { icon: 'JS',  color: '#F7DF1E', tooltip: 'JavaScript: el lenguaje del navegador. Universa y muy demandado.' },
  python:      { icon: 'PY',  color: '#3776AB', tooltip: 'Python: simple, potente. Reina en IA, Data Science y automatización.' },
  java:        { icon: 'J',   color: '#007396', tooltip: 'Java: robusto y multiplataforma. Muy usado en backend empresarial.' },
  'c++':       { icon: 'C++', color: '#00599C', tooltip: 'C++: alto rendimiento. Usado en videojuegos, sistemas y embebidos.' },
  'c#':        { icon: 'C#',  color: '#178600', tooltip: 'C#: lenguaje de Microsoft. Ecosistema .NET y desarrollo de videojuegos con Unity.' },
  c:           { icon: 'C',   color: '#555555', tooltip: 'C: el padre de los lenguajes modernos. Sistemas operativos y kernels.' },
  go:          { icon: 'Go',  color: '#00ADD8', tooltip: 'Go: concurrente y rápido. Creado por Google para servicios a escala.' },
  rust:        { icon: 'RS',  color: '#DEA584', tooltip: 'Rust: seguridad de memoria sin GC. El futuro de los sistemas de bajo nivel.' },
  kotlin:      { icon: 'KT',  color: '#7F52FF', tooltip: 'Kotlin: moderno y expresivo. Lenguaje oficial de Android.' },
  swift:       { icon: 'SW',  color: '#F05138', tooltip: 'Swift: potente y seguro. Lenguaje de Apple para iOS y macOS.' },
  ruby:        { icon: 'RB',  color: '#CC342D', tooltip: 'Ruby: elegante y expresivo. Muy usado con el framework Rails.' },
  php:         { icon: 'PHP', color: '#777BB4', tooltip: 'PHP: el caballo de batalla de la web. Mueve WordPress y muchos sitios.' },
  shell:       { icon: 'SH',  color: '#89E051', tooltip: 'Shell/Bash: automatización del sistema. Indispensable en DevOps.' },
  dart:        { icon: 'DT',  color: '#00B4AB', tooltip: 'Dart: lenguaje de Flutter. Crea apps nativas para móvil, web y desktop.' },
  r:           { icon: 'R',   color: '#198CE7', tooltip: 'R: estadística y visualización de datos. Esencial en ciencia de datos.' },
  scala:       { icon: 'SC',  color: '#DC322F', tooltip: 'Scala: funcional y orientado a objetos. Usado en Big Data con Spark.' },
  html:        { icon: 'HT',  color: '#E34F26', tooltip: 'HTML: la estructura de la web. Todo sitio comienza aquí.' },
  css:         { icon: 'CSS', color: '#264DE4', tooltip: 'CSS: el diseño de la web. Da estilo y vida a las páginas.' },
};

@Pipe({ name: 'languageIcon', standalone: true, pure: true })
export class LanguageIconPipe implements PipeTransform {
  transform(lang: string | null | undefined): LangMeta {
    if (!lang) return { icon: '?', color: '#666666', tooltip: 'Lenguaje no especificado.' };
    const key = lang.toLowerCase();
    return LANG_MAP[key] ?? { icon: lang.slice(0, 2).toUpperCase(), color: '#666666', tooltip: `Lenguaje: ${lang}` };
  }
}
