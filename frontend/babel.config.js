module.exports = {
  plugins: [
    [
      '@vue/babel-plugin-jsx',
      {
        optimize: true,
        mergeProps: true
      }
    ]
  ]
};