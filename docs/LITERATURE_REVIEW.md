# Literature review matrix

These are verified bibliographic starting points. Team reading and critical comparison are pending; rows do not imply that a member has read a paper.

| Work | Why it matters | Initial lead | Reading status | Question to resolve |
| --- | --- | --- | --- | --- |
| [Ismayilzada et al., 2025](https://aclanthology.org/2025.naacl-long.59/) | Morphological compositional generalization, including Turkish and novel roots | All three | To read | Which data-generation decisions can be reused, and how does encoder probing differ from their evaluation? |
| [Hewitt and Liang, 2019](https://aclanthology.org/D19-1275/) | Control tasks and probe memorization | Samet | To read | How should the word-type-overlap control be separated from root-disjoint evaluation? |
| [Pimentel et al., 2020](https://aclanthology.org/2020.acl-main.420/) | Information-theoretic interpretation of linguistic probing | Samet | To read | What claim does a linear probe support, and which information can it miss? |
| [BERTurk documentation](https://huggingface.co/dbmdz/bert-base-turkish-cased) | Turkish checkpoint and pretraining provenance | Fatmanur | To read | Which exact model/tokenizer revisions and data assumptions will we record? |
| [mBERT documentation](https://huggingface.co/google-bert/bert-base-multilingual-cased) | Multilingual BERT checkpoint | Fatmanur | To read | How do vocabulary and segmentation differ from BERTurk? |
| [XLM-R documentation](https://huggingface.co/FacebookAI/xlm-roberta-base) | Multilingual XLM-R checkpoint | Fatmanur | To read | How do tokenizer behavior and pretraining differences affect interpretation? |
| [Turkish-GB feature inventory](https://universaldependencies.org/treebanks/tr_gb/index.html) | Turkish feature names and possessor distinctions | Halil | To read | Which conventions transfer to our controlled nominal inventory? |
| [Zemberek-NLP](https://github.com/ahmetaa/zemberek-nlp) | Morphological analysis/generation tooling | Halil | To read | Which regular inflection classes and unknown-root behaviors are supported? |

For each paper add a short note containing: full citation; task and languages; data/source/license; models; splits; baselines; main evidence; limitations; relevance to RQ1–RQ5; exact page/section for any claim we cite. Distinguish the authors' findings from our interpretation. Add verified BibTeX to `paper/references.bib`.

Before writing a novelty claim, expand searches to encoder probing, Turkish morphological representation, nonce-word evaluation, subword segmentation, and compositional splits. Record search date/terms and closely related work here.
