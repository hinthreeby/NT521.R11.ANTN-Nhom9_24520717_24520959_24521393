#include <aconf.h>

#include <stddef.h>
#include <stdint.h>

#include "GlobalParams.h"
#include "Object.h"
#include "PDFDoc.h"
#include "Stream.h"

extern "C" void HF_ITER(const uint8_t **buf, size_t *len);

static void processInput(const uint8_t *buf, size_t len) {
  Object streamDict;
  streamDict.initNull();

  MemStream *stream = new MemStream((char *)buf, 0, (Guint)len, &streamDict);
  PDFDoc *doc = new PDFDoc(stream);
  if (doc->isOk()) {
    Object info;
    doc->getDocInfo(&info);
    info.free();

    int pages = doc->getNumPages();
    if (pages > 0) {
      doc->getPageCropWidth(1);
      doc->getPageCropHeight(1);
    }
  }
  delete doc;
}

int main() {
  globalParams = new GlobalParams(NULL);

  for (;;) {
    const uint8_t *buf;
    size_t len;
    HF_ITER(&buf, &len);
    processInput(buf, len);
  }
}
