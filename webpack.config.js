const path = require('path')

module.exports = {             // __dirname 指webpack.config.js所在目录
  mode: process.env.FLASK_ENV || 'development',
  entry: {
      comment: path.resolve(__dirname, 'app/static/components/comment/index.jsx'),
      similarity: path.resolve(__dirname, 'app/static/components/similarity.jsx'),
      recommend: path.resolve(__dirname, 'app/static/components/recommend.jsx'),
  },
  output: {
    path: path.resolve(__dirname, 'app/static/scripts'),  // 打包后文件存放的地方
    filename: '[name].entry.js'                  // 打包后输出文件的文件名
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,  // 匹配loaders所处理文件的扩展名的正则表达式(必须)
        exclude: /node_modules/,  // 不需要打包的文件夹(可选)
        use: {
          loader: 'babel-loader',  // loader的名称(必须)
          options: {  // 为loaders提供的额外的设置选项(可选)，也可在项目目录下使用.babelrc进行配置
            presets: ['env', 'react', 'stage-2']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  }
}
