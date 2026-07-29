---
name: Bug report
title: "[Bug] "
description: Report a bug in SpecOmega
labels: bug
body:
  - type: textarea
    id: description
    attributes:
      label: Description
      description: What happened?
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: How can the issue be reproduced?
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
