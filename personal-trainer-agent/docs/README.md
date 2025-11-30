# Documentation

## Guides

- [Getting Started](getting-started.md)
- [Training Methods](training-methods.md)
- [Evaluation Guide](evaluation-guide.md)
- [API Reference](api-reference.md)

## Examples

See the `examples/` directory for complete examples:

- Basic analysis and evaluation
- Prompt optimization
- TRL training with DPO
- Session management
- Custom evaluators

## Architecture

The Personal Trainer Agent follows a modular architecture:

1. **Analyzers** - Examine agent outputs to compute performance metrics and detect weaknesses
2. **Evaluators** - Score outputs against rubrics or compare against baselines
3. **Trainers** - Apply improvements through prompt optimization or RL training
4. **Utils** - Track sessions and metrics across training iterations

## Workflow

1. **Collect** agent outputs from your target agent
2. **Analyze** to identify performance characteristics and weaknesses
3. **Evaluate** against rubrics or baselines
4. **Plan** improvements based on analysis
5. **Train** using prompt optimization or RL
6. **Verify** improvements with re-evaluation
7. **Iterate** until performance goals are met
